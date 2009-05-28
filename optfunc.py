from optparse import OptionParser, make_option
import sys, inspect

class ErrorCollectingOptionParser(OptionParser):
    def __init__(self, *args, **kwargs):
        self._errors = []
        # can't use super() because OptionParser is an old style class
        OptionParser.__init__(self, *args, **kwargs)
    
    def error(self, msg):
        self._errors.append(msg)

def func_to_optionparser(func):
    args, varargs, varkw, defaultvals = inspect.getargspec(func)
    defaultvals = defaultvals or ()
    options = dict(zip(args[-len(defaultvals):], defaultvals))
    if defaultvals:
        required_args = args[:-len(defaultvals)]
    else:
        required_args = args
    
    # Now build the OptionParser
    opt = ErrorCollectingOptionParser(usage = func.__doc__)
    for name, example in options.items():
        short_name = '-%s' % name[0]
        long_name = '--%s' % name.replace('_', '-')
        if example in (True, False, bool):
            action = 'store_true'
        else:
            action = 'store'
        opt.add_option(make_option(
            short_name, long_name, action=action, dest=name, default=example
        ))
    
    return opt, required_args

def resolve_args(func, argv):
    parser, required_args = func_to_optionparser(func)
    options, args = parser.parse_args(argv)
    
    # Do we have correct number af required args?
    if len(required_args) != len(args):
        raise TypeError, 'Requires %d arguments, got %d' % (
            len(required_args), len(args)
        )
    
    for i, name in enumerate(required_args):
        setattr(options, name, args[i])
    
    return options.__dict__, parser._errors

def run(func, argv=None):
    argv = argv or sys.argv[1:]
    resolved, errors = resolve_args(func, argv)
    if not errors:
        return func(**resolved)
    else:
        print "ERRORS: %s" % errors
