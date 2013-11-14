import builtins
import functools
import operator

__all__ = ['_1', '_2', '_3', '_']

class Lambda(object):
    def __init__(self, func, name=None):
        self.func = func
        if name is None:
            self.__name__ = repr(self.func)
        else:
            self.__name__ = name
    def __repr__(self):
        return self.__name__
    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

class Placeholder(Lambda):
    def __init__(self, index=None, name=None):
        if name is None:
            name = str(index)
        name = '_{}'.format(name)
        self.index = index - 1
        super().__init__((lambda *args: args[self.index]), name)
    def __call__(self, *args, **kwargs):
        @functools.wraps(self.value)
        def wrapped(*a):
            def argify(arg):
                if isinstance(arg, MagicPlaceholder):
                    return arg.value
                elif isinstance(arg, Placeholder):
                    return a[arg.index]
                else:
                    return arg
            return args[self.index](*map(argify, args), **kwargs)
        argspec = ', '.join([repr(arg) for arg in args] + 
                            ['{}={!r}'.format(kv) for kv in kwargs.items()])
        name = '_({})({})'.format(self, argspec)
        return Lambda(wrapped, name)        

class MagicPlaceholder(Placeholder):
    def __init__(self, value):
        super().__init__(0, '({})'.format(value))
        self.value = value
    def __call__(self, *args, **kwargs):
        if not callable(self.value):
            return super().__call__(*args, **kwargs)
        @functools.wraps(self.value)
        def wrapped(*a):
            def argify(arg):
                if isinstance(arg, MagicPlaceholder):
                    return arg.value
                elif isinstance(arg, Placeholder):
                    return a[arg.index]
                else:
                    return arg
            return self.value(*map(argify, args), **kwargs)
        argspec = ', '.join([repr(arg) for arg in args] + 
                            ['{}={!r}'.format(kv) for kv in kwargs.items()])
        name = '_({})({})'.format(self.value.__name__, argspec)
        return Lambda(wrapped, name)

def make_bunop(name, symbol=None, pattern='{}({})', dunder = None):
    if symbol is None:
        symbol = name
    if dunder is None:
        dunder = '__{}__'.format(name)
    op = getattr(builtins, name)
    
    @functools.wraps(op)
    def wrapper(self):
        f = lambda *args: op(args[self.index])
        return Lambda(f, pattern.format(symbol, self))
    setattr(Placeholder, dunder, wrapper)

    @functools.wraps(op)
    def mwrapper(self):
        f = lambda *args: op(self.value)
        return Lambda(f, pattern.format(symbol, self))
    setattr(MagicPlaceholder, dunder, wrapper)

def make_unop(name, symbol=None, pattern='{}{}', module=operator):
    if symbol is None:
        symbol = name
    dunder = '__{}__'.format(name)
    op = getattr(module, dunder, None)
    if not op:
        op = getattr(module, name)
    
    @functools.wraps(op)
    def wrapper(self):
        f = lambda *args: op(args[self.index])
        return Lambda(f, pattern.format(symbol, self))
    setattr(Placeholder, dunder, wrapper)

    @functools.wraps(op)
    def mwrapper(self):
        f = lambda *args: op(self.value)
        return Lambda(f, pattern.format(symbol, self))
    setattr(MagicPlaceholder, dunder, wrapper)

def make_binop(name, symbol=None, pattern='{} {} {}', module=operator,
               r=False, i=False):
    # can't do __ifoo__ because they're not expressions
    #if i:
    #    make_binop('i' + name, symbol + '=', pattern)

    if symbol is None:
        symbol = name
    dunder = '__{}__'.format(name)
    rdunder = '__r{}__'.format(name)
    op = getattr(module, dunder, None)
    if not op:
        op = getattr(module, name)
    
    @functools.wraps(op)
    def wrapper(self, rhs):
        if isinstance(rhs, MagicPlaceholder):
            f = lambda *args: op(args[self.index], rhs.value)
        elif isinstance(rhs, Placeholder):
            f = lambda *args: op(args[self.index], args[rhs.index])
        else:
            f = lambda *args: op(args[self.index], rhs)
        return Lambda(f, pattern.format(self, symbol, rhs))
    setattr(Placeholder, dunder, wrapper)

    @functools.wraps(op)
    def rwrapper(self, lhs):
        if isinstance(lhs, MagicPlaceholder):
            f = lambda *args: op(lhs.value, args[self.index])
        elif isinstance(lhs, Placeholder):
            f = lambda *args: op(args[lhs.index], args[self.index])
        else:
            f = lambda *args: op(lhs, args[self.index])
        return Lambda(f, pattern.format(lhs, symbol, self))
    rwrapper.__name__ = rdunder
    if r:
        setattr(Placeholder, rdunder, rwrapper)

    @functools.wraps(op)
    def mwrapper(self, rhs):
        if isinstance(rhs, MagicPlaceholder):
            f = lambda *args: op(self.value, rhs.value)
        elif isinstance(rhs, Placeholder):
            f = lambda *args: op(self.value, args[rhs.index])
        else:
            f = lambda *args: op(self.value, rhs)
        return Lambda(f, pattern.format(self, symbol, rhs))
    setattr(MagicPlaceholder, dunder, mwrapper)

    @functools.wraps(op)
    def mrwrapper(self, lhs):
        if isinstance(lhs, MagicPlaceholder):
            f = lambda *args: op(lhs.value, self.value)
        elif isinstance(lhs, Placeholder):
            f = lambda *args: op(args[lhs.index], self.value)
        else:
            f = lambda *args: op(lhs, self.value)
        return Lambda(f, pattern.format(lhs, symbol, self))
    mrwrapper.__name__ = rdunder
    if r:
        setattr(MagicPlaceholder, rdunder, rwrapper)

make_unop('next', pattern='{}({})', module=builtins)

make_binop('getattr', '.', pattern='{}{}{}', module=builtins)

make_binop('lt', '<')
make_binop('le', '<=')
make_binop('eq', '==')
make_binop('ne', '!=')
make_binop('ge', '>=')
make_binop('gt', '>')

make_unop('abs', 'abs', pattern='{}({})')
make_binop('add', '+', r=True, i=True)
make_binop('and', '&', r=True, i=True)
make_binop('floordiv', '//', r=True, i=True)
make_unop('index', '__index__', pattern='{}.{}()')
make_unop('invert', '~')
make_binop('lshift', '<<')
make_binop('mod', '%', r=True, i=True)
make_binop('mul', '*', r=True, i=True)
make_unop('neg', '-')
make_binop('or', '|', r=True, i=True)
make_unop('pos', '+')
make_binop('pow', '**', r=True, i=True)
make_binop('rshift', '>>')
make_binop('sub', '-', r=True, i=True)
make_binop('truediv', '/', r=True, i=True)
make_binop('xor', '^', r=True, i=True)

# can't do __contains__ because at least CPython converts the result to bool

make_binop('getitem', pattern='{0}[{2}]')
# can't do __setitem__ and __delitem__ because they're not expressions

_1 = Placeholder(1)
_2 = Placeholder(2)
_3 = Placeholder(3)
_ = MagicPlaceholder
_v = MagicPlaceholder

