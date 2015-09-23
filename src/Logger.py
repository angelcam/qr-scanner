import json
import sys
from syslog import syslog, openlog

#Simple syslog logging module
#Usage:
#from  Logger import logger
#log.start("myAppName")
#log.set_min_level(log.INFO)
#log.log(logger.INFO, "This is log message.")

class Logger(object):

    #logging levels
    DEBUG = 0
    INFO = 1
    ERROR = 2
    FATAL = 3

    stringToLevel = {"debug": DEBUG, "info": INFO, "error": ERROR, "fatal": FATAL}

    def __init__(self):
        self._metadata = {}
        self._minLevel = self.DEBUG
        self._write_output = False

        self._levelDict = {0:"debug", 1:"info", 2:"error", 3:"fatal"}

    def start(self, appName):
        openlog(appName)

    def log(self, level, message, metadata=None):

        if(level < self._minLevel):
            return

        levelStr = self._levelDict.get(level, None)
        if(not levelStr):
            logdata = { 'message': "Logger.log: Bad log level. Cannot log message " + message, 'level': 'info' }
            syslog(json.dumps(logdata))
            return

        logdata = { 'message': message, 'level': levelStr}
        if metadata:
            logdata.update(metadata)
        syslog(json.dumps(logdata))
        if(self._write_output):
            print(logdata)
            sys.stdout.flush()

    #val = True / False
    def set_output_writing(self, val):
        self._write_output = val

    def set_min_level(self, level):
        self._minLevel = level

    def set_metadata(self, key, value):
        self._metadata[key] = value

    def remove_metadata(self, key):
        del self._metadata[key]

#create singleton
log = Logger()