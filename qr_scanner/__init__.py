import threading
import ctypes
import ctypes.util
import logging
import sys

from abc import ABC
from ctypes import c_char_p, c_int, c_size_t, c_uint8, c_uint64, c_void_p, CDLL, CFUNCTYPE, POINTER
from typing import Optional

logger = logging.getLogger(__name__)


class Library(ABC):
    """
    Native library loader.
    """

    def __init__(self):
        if sys.platform == 'linux':
            lib_name = 'lib{}.so'.format(self.library)
        else:
            raise Exception("Unsupported platform: " + sys.platform)

        self.lib = CDLL(lib_name)

        self.load_symbols()

    def load_symbols(self):
        """
        A function that's called on instance initialization. It should be used
        by sub-classes to load any native symbols from the library.
        """
        pass

    def load_function(self, name, argtypes=[], restype=None):
        """
        Load a given native function and create a field of the same name.,
        """
        function = getattr(self.lib, name)
        function.argtypes = list(argtypes)
        function.restype = restype
        setattr(self, name, function)

    def load_functions(self, functions):
        """
        Load all given native functions and create fields of the same name.
        The method expect an iterable of function descriptions, where function
        description is a triplet (name, argtypes, restype).
        """
        for function in functions:
            self.load_function(*function)


class QRScannerLibrary(Library):
    """
    Loader for libqr_scanner.
    """

    library = 'qr_scanner'

    LOG_LEVEL_DEBUG = 1
    LOG_LEVEL_INFO = 2
    LOG_LEVEL_WARN = 3
    LOG_LEVEL_ERROR = 4

    LOG_CALLBACK = CFUNCTYPE(None, c_void_p, c_char_p, c_int, c_int, c_char_p)

    def __init__(self):
        super().__init__()

        def log_callback(opaque, file, line, level, msg):
            if level < self.LOG_LEVEL_DEBUG:
                return
            file = file.decode('utf-8')
            msg = msg.decode('utf-8')
            logger.debug(msg, extra={
                'file': '{}:{}'.format(file, line),
            })

        self.__log_callback = self.LOG_CALLBACK(log_callback)

        self.qrs__set_log_callback(self.__log_callback, None)

    def load_symbols(self):
        self.load_functions((
            ('qrs__set_log_callback', [self.LOG_CALLBACK, c_void_p]),

            ('qrs__scanner_config__new', [], c_void_p),
            ('qrs__scanner_config__free', [c_void_p]),
            ('qrs__scanner_config__key_frames_only', [c_void_p, c_int]),

            ('qrs__scanner__scan_http_stream', [c_char_p, c_uint64, c_void_p], c_void_p),
            ('qrs__scanner__free', [c_void_p]),
            ('qrs__scanner__next_qr_code', [c_void_p], c_void_p),

            ('qrs__qr_code__free', [c_void_p]),
            ('qrs__qr_code__get_data', [c_void_p], POINTER(c_uint8)),
            ('qrs__qr_code__get_data_size', [c_void_p], c_size_t),
        ))


lib = QRScannerLibrary()


class NativeObject:
    """
    Abstraction over a native object. The memory will be released automatically
    by garbage collector if a free_func is given and the underlying raw pointer
    hasn't been transferred using the into_raw_ptr() method.
    """

    def __init__(self, raw_ptr: c_void_p, free_func=None):
        self.__raw_ptr = raw_ptr
        self.__free_func = free_func
        self.__free_lock = None if free_func is None else threading.Lock()

    def __del__(self):
        if self.__free_func is None:
            return
        if self.__raw_ptr is None:
            return

        with self.__free_lock:
            if self.__raw_ptr is not None:
                self.__free_func(self.__raw_ptr)
            self.__raw_ptr = None

    @property
    def raw_ptr(self) -> c_void_p:
        return self.__raw_ptr

    def call_method(self, native_func, *args):
        assert self.__raw_ptr is not None
        return native_func(self.__raw_ptr, *args)


class ScannerConfig(NativeObject):

    def __init__(self):
        ptr = lib.qrs__scanner_config__new()
        assert ptr is not None
        super().__init__(ptr, free_func=lib.qrs__scanner_config__free)
        self.key_frames_only = False

    @property
    def key_frames_only(self) -> bool:
        return self.__key_frames_only

    @key_frames_only.setter
    def key_frames_only(self, v: bool):
        self.__key_frames_only = v
        self.call_method(lib.qrs__scanner_config__key_frames_only, self.__key_frames_only)


class Scanner(NativeObject):

    def __init__(self, raw_ptr: c_void_p):
        super().__init__(raw_ptr, free_func=lib.qrs__scanner__free)

    @classmethod
    def scan_http_stream(cls, url: str, stop_after: Optional[float] = None, config: Optional[ScannerConfig] = None):
        url = url.encode('utf-8')
        if stop_after is None:
            stop_after = 0
        stop_after = int(stop_after * 1000)
        config = None if config is None else config.raw_ptr
        ptr = lib.qrs__scanner__scan_http_stream(url, stop_after, config)
        if ptr is None:
            raise ScannerError("Unable to scan a given URL")
        return cls(ptr)

    def next_qr_code(self) -> Optional[bytes]:
        ptr = self.call_method(lib.qrs__scanner__next_qr_code)
        if ptr is None:
            return None

        try:
            data_ptr = lib.qrs__qr_code__get_data(ptr)
            data_size = lib.qrs__qr_code__get_data_size(ptr)

            data = bytes(ctypes.string_at(data_ptr, data_size))
        finally:
            lib.qrs__qr_code__free(ptr)

        return data


class ScannerError(Exception):
    pass


def scan(stream_url: str, timeout: Optional[float] = None, log_extra: Optional[dict] = None):
    log_extra = log_extra or {}

    logger.info("Scanning QR codes", extra=log_extra)

    config = ScannerConfig()
    config.key_frames_only = True

    try:
        scanner = Scanner.scan_http_stream(stream_url, timeout, config)
        discovered = set()
        while True:
            code = scanner.next_qr_code()
            if code is None:
                return
            elif code not in discovered:
                discovered.add(code)
                yield code
    except ScannerError as e:
        logger.error("Scanner exited with error", extra={
            'cause': str(e),
            **log_extra,
        })
    finally:
        logger.info("Scanning ended", extra=log_extra)
