[loggers]
keys=root,importapi,deleteapi,analyticsapi,schedulerapi,filestructurecheckapi,eventapi,werkzeug

[handlers]
keys=consoleHandler, fileHandler

[formatters]
keys=simpleFormatter

[logger_root]
level=${LOG_LEVEL}
handlers=consoleHandler, fileHandler

[logger_werkzeug]
level=WARNING
handlers=consoleHandler, fileHandler
qualname=werkzeug
propagate=0

[logger_importapi]
level=${LOG_LEVEL}
handlers=consoleHandler, fileHandler
qualname=importapi
propagate=0

[logger_deleteapi]
level=${LOG_LEVEL}
handlers=consoleHandler, fileHandler
qualname=deleteapi
propagate=0

[logger_analyticsapi]
level=${LOG_LEVEL}
handlers=consoleHandler, fileHandler
qualname=analyticsapi
propagate=0

[logger_schedulerapi]
level=${LOG_LEVEL}
handlers=consoleHandler, fileHandler
qualname=schedulerapi
propagate=0

[logger_filestructurecheckapi]
level=${LOG_LEVEL}
handlers=consoleHandler, fileHandler
qualname=schedulerapi
propagate=0

[logger_eventapi]
level=${LOG_LEVEL}
handlers=consoleHandler, fileHandler
qualname=schedulerapi
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=DEBUG
formatter=simpleFormatter
args=(sys.stdout,)

[handler_fileHandler]
class = FileHandler
args = ('/var/log/gis.log','a')
level = NOTSET
formatter = simpleFormatter

[formatter_simpleFormatter]
format=%(asctime)s %(levelname)-5.5s [%(name)s:%(lineno)d] %(message)s
datefmt=