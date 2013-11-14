quicklambda
===========

An expression template library for building "quick lambdas", like `5 + _1`.

Any expression involving a placeholder (`_1`, `_2`, or `_3`), or a value 
wrapped by the `_` function, becomes a function. For example, all of the
function calls below print out 3:

    from quicklambda import *
    add1 = _1 + 1
    print(add1(2))
    add1 = 1 + _1
    print(add1(2))
    add1 = _2 + 1
    print(add1(None, 2))
    add = _1 + _2
    print(add(1, 2))
    add = _(1) + 2
    print(add())
    add1 = _(add)(_1, 1)
    print(add1(2))
    
Expressions
===========

Placeholders
------------

`_1`, `_2`, and `_3` are placeholders that take on the value of
the first, second, and third arguments when the lambda expression 
function is eventually called. (Extending this beyond 3 would be
trivial, but how often will you need it?)

There is currently no syntax for keyword placeholders, mostly
because I haven't thought of anything good.

`_` is a function that turns any value into a placeholder for
itself--that is, `_(foo)` takes on the value of `foo` when the
lambda expression is eventually called. This is primarily useful
to handle cases where placeholder operator overloading doesn't
work, as described below, or where you have no placeholders
(e.g., because you're building a lambda expression with no
arguments).

It should also be possible to wrap an expression with _ to
turn it into a placeholder (which you would mainly do to build
complex call expressions), but **this generally does not work**
in the current version.

Because the name `_` is useless in the interactive prompt (each
time you execute an expression statement, `_` is rebound to the
value), it's also available as `_v`. Which is hideous, but I
haven't thought of anything better yet.

Note that `_(foo)` stores the _value_ of `foo`, not the `variable`.
This should be fixable by either passing the name as a string, or by
using a different function (named what?) that uses frame hacks to 
find the name of its argument, but both of those have major flaws,
so I haven't implemented either yet. If you want a function with
a mutable closure, you'll have to use `def`+`nonlocal` (or `lambda`
with the default value hack), not a lambda expression.

Attribute access
----------------

Works with a placeholder on the left. Does not work with a
placeholder on the right (even if there's also a placeholder on the 
left). So, `_1.foo` is a function, but `foo._1` is not, and the 
`_(foo)._1` trick used elsewhere will not help, and neither is
`_1._2`. (This might be fixable; I haven't thought it through.)

Note that this includes methods as well as data attributes, but
the function returns the method, it doesn't call it. So, 
`_1.meth(obj)` is often not what you want, but it's what you get.
(There may be some syntax that makes sense here, but I'm not sure
what it is.)

Unary operators
---------------

`-`, `+`, `~`: Work. `-_1` is a function.

`not`: Does not work (because it effectively calls `bool`; see
Special methods below).

Binary operators
----------------

`+`, `-`, `*`, `/`, `//`, `%`, `**`, `&`, `|`, `^`: Work, in both
directions, except that a few types do not work on the left side. 
`_1 + 1`, `1 + _1`, and `_1 + _2` are all functions. Note that 
`+=`, `-=`, etc. cannot be used, because they are not expressions.

`<`, `<=`, `==`, `!=`, `>=`, `>`: Work, in both directions, with
slightly different types that don't work on the left side. Also,
note that `1 < _1` becomes `_1 > 1`, and so on.

`<<`, `>>`: Work with the placeholder on the left. So `_1 << 1`
is a function, but `1 << _1` is not. (Use `_(1) << _1`.) Note that
`<<=` and `>>=` cannot be used, because they are not expressions.

`[]`: Works with the placeholder on the left. So `_1[1]` is a
function, but `arr[_1]` is not. (Use `_(arr)[_1]`.) Slicing works,
but a placeholder used as the start or step of a slice does not
(so `_1[:_2]` is fine, but `_1[_2:]` is not). (This may be a
peculiarity of CPython, and it might change in a later version.)
Note that the set and del versions `_1[1] = 2` and `del _1[1]` do 
not work because they are not expressions.

`()`: Works with the placeholder on the left. So `_1(1)` is a
function, but `foo(_1)` is not. (Use `_(foo)(_1)`.) Certain special
functions work differently; see Special Functions below. Note that 
call expressions can be confusing, because calling a placeholder 
creates a function, but calling an expression made with a placeholder 
_calls_ the function. (To make a call expression function out of an
expression function, you have to wrap it in `_`, which can easily
become unreadable very quickly.) Also, remember that if you wanted
`foo(_1)` you can usually just use `foo` directly (but of course
`foo(1, _1)` would be a nice way to create quick partials).

`in`: Does not work, because the return value is forcibly converted
to bool.

`is`: Does not work, because it's not overridable.

Special functions
-----------------

`abs`, `next`: Work. `abs(_1)` is a function.

`bool`, `int`, `float`, `bytes`, `len`, `iter`: Do not work, because
they require a return value of a specific type. (Note that `bool`
and `len` not working means that any lambda expression is considered
True in a boolean context.)

`str`, `repr`: Do not work, because that would cause infinite
recursion trying to print a lambda expression.

`__index__`: Works, but there's no function to call it with.

Any special functions defined by other stdlib modules (like
pickle's `__reduce__`) or third-party modules have not been
implemented.

In most cases, lack of support for a special function is not a
problem, as you can `_`-wrap them--or, of course, just use the
function directly.

Complex expressions
-------------------

Any expression that works with a placeholder should usually also 
work with an expression function, except the special case of call
expressions. And you can always handle the cases that don't with
the `_` function.

However, **this generally does not work** in the current version.

Future
======

* If there are any missing operators, finding and adding them is
an obvious goal.

* Making complex expressions work, automatically and in the `_`
function, is on the queue.

* Keyword placeholders and a better name for `_v` are just waiting
for me to come up with something that looks nice.

* Wrapping names/closures instead of only values needs both a
nice-looking syntax and an implementation that's not as horrible
as the one I wrote when I last attempted this a few years ago.

* The first version of this module auto-generated all of the ugly
stuff in the wrapper-maker functions. I'd like to factor out the
repetition if possible, or go back to the auto-generated code if
not.

* I think the three classes can be collapsed into two.
