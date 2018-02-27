import logging

from qr_scanner import utils, config


class LoggerWithCameraContext(logging.Logger):
    def __init__(self, stream_url, level=config.LOG_LEVEL):
        super().__init__('qr_scanner', level)
        self.context = {
            'camera_url': stream_url,
            'camera_id': utils.cam_id_from_url(stream_url)
        }

    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False):
        if extra is None:
            extra = {}
        extra.update(self.context)
        super()._log(level, msg, args, exc_info, extra, stack_info)