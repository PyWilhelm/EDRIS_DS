from BuilderService.BuilderService import app
from conf import __conf__

print "after main"
#import logging
#logging.basicConfig(level=logging.DEBUG)
app.run(host=__conf__['buildSetting']['host'], port=__conf__['buildSetting']['port'],
        threaded=True, debug=False, 
        ssl_context=(__conf__['buildSetting']['certfile'], __conf__['buildSetting']['keyfile']))