# Decorator logging 
import functools, logging
from datetime import datetime
import gzip, traceback

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def format_arg_value(arg_val):
    """ Return a string representing a (name, value) pair.
    
    >>> format_arg_value(('x', (1, 2, 3)))
    'x=(1, 2, 3)'
    """
    arg, val = arg_val
    return "%s=%r" % (arg, val)

class log_with(object):
    '''Logging decorator that allows you to log with a
    specific logger.
    '''
    ENTRY_MESSAGE = "{0}: Entering {1}({2})"
    ERROR_MESSAGE = "{0}: Error at {1}: ({2})"
    EXIT_MESSAGE = '{0}: Exiting {1}({2}) returning: {3}'

    def __init__(self, logger=None):
        self.logger = logger

    def __call__(self, fn):
        if not self.logger:
            logging.basicConfig()
            self.logger = logging.getLogger(fn.__module__)

        import functools
        code = fn.func_code
        argcount = code.co_argcount
        argnames = code.co_varnames[:argcount]
        fn_defaults = fn.func_defaults or list()
        argdefs = dict(zip(argnames[-len(fn_defaults):], fn_defaults))
        
        @functools.wraps(fn)
        def wrapped(*v, **k):
            # Collect function arguments by chaining together positional,
            # defaulted, extra positional and keyword arguments.
            positional = map(format_arg_value, zip(argnames, v))
            defaulted = [format_arg_value((a, argdefs[a]))
                         for a in argnames[len(v):] if a not in k]
            nameless = map(repr, v[argcount:])
            keyword = map(format_arg_value, k.items())
            args = positional + defaulted + nameless + keyword
            self.logger.info(self.ENTRY_MESSAGE.format(str(datetime.now()), fn.__name__, ", ".join(args)))
            try: 
                f_result = fn(*v, **k)
            except Exception as err:
                self.logger.info(self.ERROR_MESSAGE.format(str(datetime.now()), fn.__name__, traceback.format_exc()))
                raise err
            self.logger.info(self.EXIT_MESSAGE.format(str(datetime.now()), fn.__name__, ", ".join(args), str(f_result)))
            return f_result
        return wrapped

def get_logger(name):
    logger = logging.getLogger(name)
    z_file = gzip.open(name + '.log.gz', mode='wb')
    logger.addHandler(logging.StreamHandler(z_file))
    logger.setLevel(logging.DEBUG)

    return logger

if __name__ == '__main__':
    logging.basicConfig()
    log = logging.getLogger('custom_log')
    log.setLevel(logging.DEBUG)
    log.info('started logging')

    @log_with(log) 
    def foo():
        print 'this is foo'
        return 'string 1', 4234
    foo()

    @log_with() 
    def foo2():
        print 'this is foo2'
    foo2()
