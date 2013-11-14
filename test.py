from quicklambda import *

def test(expr):
    print('{}: {}'.format(expr, expr(1, 2, 3)))

test(_1 + 1)
test(1 + _1)
test(_(1))
test(_2 + 1)
test(_1 + _2)
test(_(1) + _(2))
test(_1 + _(1))
test(_(1) + _1)

test(_1 - 1)
test(1 - _1)
test(_2 - 1)
test(_1 - _2)
test(_(1) - _(2))
test(_1 - _(1))
test(_(1) - _1)

test(_([10,20,30])[_1])

test(_(print))
test(_(print)(0))
test(_(print)(_1))

add = _1 + _2
test(add)
add1 = _(add)(_1, 1)
test(add1)

