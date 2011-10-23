from __future__ import division
from sympy import (Abs, Catalan, cos, Derivative, E, EulerGamma, exp, factorial,
    Function, GoldenRatio, I, Integer, Integral, Interval, Lambda, Limit, log,
    Matrix, nan, O, oo, pi, Rational, Float, Rel, S, sin, SparseMatrix, sqrt,
    summation, Sum, Symbol, symbols, Wild, WildFunction, zeta, zoo,
    Dummy, Dict)
from sympy.core import Expr
from sympy.physics.units import second, joule
from sympy.polys import Poly, RootOf, RootSum, groebner
from sympy.statistics.distributions import Normal, Sample, Uniform
from sympy.geometry import Point, Circle

from sympy.utilities.pytest import XFAIL, raises

from sympy.printing import sstr, sstrrepr, StrPrinter

x, y, z, w = symbols('x,y,z,w')
d = Dummy('d')

def test_printmethod():
    class R(Abs):
        def _sympystr(self, printer):
            return "foo(%s)" % printer._print(self.args[0])
    assert sstr(R(x)) == "foo(x)"
    class R(Abs):
        def _sympystr(self, printer):
            return "foo"
    assert sstr(R(x)) == "foo"

def test_Abs():
    assert str(Abs(x)) == "Abs(x)"
    assert str(Abs(Rational(1,6))) == "1/6"
    assert str(Abs(Rational(-1,6))) == "1/6"

def test_Add():
    assert str(x+y) == "x + y"
    assert str(x+1) == "x + 1"
    assert str(x+x**2) == "x**2 + x"
    assert str(5+x+y+x*y+x**2+y**2) == "x**2 + x*y + x + y**2 + y + 5"
    assert str(1+x+x**2/2+x**3/3) == "x**3/3 + x**2/2 + x + 1"
    assert str(2*x-7*x**2 + 2 + 3*y) == "-7*x**2 + 2*x + 3*y + 2"
    assert str(x-y) == "x - y"
    assert str(2-x) == "-x + 2"
    assert str(x-2) == "x - 2"
    assert str(x-y-z-w) == "-w + x - y - z"
    assert str(x-z*y**2*z*w) == "-w*y**2*z**2 + x"
    assert str(x-1*y*x*y) == "-x*y**2 + x"
    assert str(sin(x).series(x, 0, 15)) == "x - x**3/6 + x**5/120 - x**7/5040 + x**9/362880 - x**11/39916800 + x**13/6227020800 + O(x**15)"

def test_Catalan():
    assert str(Catalan) == "Catalan"

def test_ComplexInfinity():
    assert str(zoo) == "zoo"

def test_Derivative():
    assert str(Derivative(x, y)) == "Derivative(x, y)"
    assert str(Derivative(x**2, x, evaluate=False)) == "Derivative(x**2, x)"
    assert str(Derivative(x**2/y, x, y, evaluate=False)) == "Derivative(x**2/y, x, y)"

def test_dict():
    assert str({1: 1+x}) == sstr({1: 1+x}) == "{1: x + 1}"
    assert str({1: x**2, 2: y*x}) in ("{1: x**2, 2: x*y}", "{2: x*y, 1: x**2}")
    assert sstr({1: x**2, 2: y*x}) == "{1: x**2, 2: x*y}"

def test_Dict():
    assert str(Dict({1: 1+x})) == sstr({1: 1+x}) == "{1: x + 1}"
    assert str(Dict({1: x**2, 2: y*x})) in (
            "{1: x**2, 2: x*y}", "{2: x*y, 1: x**2}")
    assert sstr(Dict({1: x**2, 2: y*x})) == "{1: x**2, 2: x*y}"

def test_Dummy():
    assert str(d) == "_d"
    assert str(d+x) == "_d + x"

def test_EulerGamma():
    assert str(EulerGamma) == "EulerGamma"

def test_Exp():
    assert str(E) == "E"

def test_factorial():
    n = Symbol('n', integer=True)
    assert str(factorial(-2)) == "0"
    assert str(factorial(0)) == "1"
    assert str(factorial(7)) == "5040"
    assert str(factorial(n)) == "n!"
    assert str(factorial(2*n)) == "(2*n)!"

def test_Function():
    f = Function('f')
    fx = f(x)
    w = WildFunction('w')
    assert str(f) == "f"
    assert str(fx) == "f(x)"
    assert str(w) == "w_"

def test_Geometry():
    assert sstr(Point(0,0))  == 'Point(0, 0)'
    assert sstr(Circle(Point(0,0), 3))   == 'Circle(Point(0, 0), 3)'
    # TODO test other Geometry entities

def test_GoldenRatio():
    assert str(GoldenRatio) == "GoldenRatio"

def test_ImaginaryUnit():
    assert str(I) == "I"

def test_Infinity():
    assert str(oo) == "oo"
    assert str(I * oo) == "oo*I"

def test_Integer():
    assert str(Integer(-1)) == "-1"
    assert str(Integer(1)) == "1"
    assert str(Integer(-3)) == "-3"
    assert str(Integer(0)) == "0"
    assert str(Integer(25)) == "25"

def test_Integral():
    assert str(Integral(sin(x), y)) == "Integral(sin(x), y)"
    assert str(Integral(sin(x), (y, 0, 1))) == "Integral(sin(x), (y, 0, 1))"

def test_Interval():
    a = Symbol('a', real=True)
    assert str(Interval(0, a)) == "[0, a]"
    assert str(Interval(0, a, False, False)) == "[0, a]"
    assert str(Interval(0, a, True, False)) == "(0, a]"
    assert str(Interval(0, a, False, True)) == "[0, a)"
    assert str(Interval(0, a, True, True)) == "(0, a)"

def test_Lambda():
    assert str(Lambda(d, d**2)) == "Lambda(_d, _d**2)"

def test_Limit():
    assert str(Limit(sin(x)/x, x, y)) == "Limit(sin(x)/x, x, y)"
    assert str(Limit(1/x, x, 0)) == "Limit(1/x, x, 0)"
    assert str(Limit(sin(x)/x, x, y, dir="-")) == "Limit(sin(x)/x, x, y, dir='-')"

def test_list():
    assert str([x]) == sstr([x]) == "[x]"
    assert str([x**2, x*y+1]) == sstr([x**2, x*y+1]) == "[x**2, x*y + 1]"
    assert str([x**2, [y+x]]) == sstr([x**2, [y+x]]) == "[x**2, [x + y]]"

def test_Matrix():
    M = Matrix([[x**+1, 1], [y, x+y]])
    assert str(M) == sstr(M) == "[x,     1]\n[y, x + y]"
    M = Matrix()
    assert str(M) == sstr(M) == "[]"
    M = Matrix(0, 1, lambda i, j: 0)
    assert str(M) == sstr(M) == "[]"

def test_Mul():
    assert str(x/y) == "x/y"
    assert str(y/x) == "y/x"
    assert str(x/y/z) == "x/(y*z)"
    assert str((x+1)/(y+2)) == "(x + 1)/(y + 2)"
    assert str(2*x/3)  ==  '2*x/3'
    assert str(-2*x/3)  == '-2*x/3'

    class CustomClass1(Expr):
        pass
    class CustomClass2(Expr):
        pass
    cc1 = CustomClass1(commutative=True)
    cc2 = CustomClass2(commutative=True)
    assert str(Rational(2)*cc1) == '2*CustomClass1()'
    assert str(cc1*Rational(2)) == '2*CustomClass1()'
    assert str(cc1*Float("1.5")) == '1.5*CustomClass1()'
    assert str(cc2*Rational(2)) == '2*CustomClass2()'
    assert str(cc2*Rational(2)*cc1) == '2*CustomClass1()*CustomClass2()'
    assert str(cc1*Rational(2)*cc2) == '2*CustomClass1()*CustomClass2()'

def test_NaN():
    assert str(nan) == "nan"

def test_NegativeInfinity():
    assert str(-oo) == "-oo"

def test_Normal():
    assert str(Normal(x+y, z)) == "Normal(x + y, z)"

def test_Order():
    assert str(O(x)) == "O(x)"
    assert str(O(x**2)) == "O(x**2)"
    assert str(O(x*y)) == "O(x*y, x, y)"

def test_Pi():
    assert str(pi) == "pi"

def test_Poly():
    assert str(Poly(0, x)) == "Poly(0, x, domain='ZZ')"
    assert str(Poly(1, x)) == "Poly(1, x, domain='ZZ')"
    assert str(Poly(x, x)) == "Poly(x, x, domain='ZZ')"

    assert str(Poly(2*x + 1, x)) == "Poly(2*x + 1, x, domain='ZZ')"
    assert str(Poly(2*x - 1, x)) == "Poly(2*x - 1, x, domain='ZZ')"

    assert str(Poly(-1, x)) == "Poly(-1, x, domain='ZZ')"
    assert str(Poly(-x, x)) == "Poly(-x, x, domain='ZZ')"

    assert str(Poly(-2*x + 1, x)) == "Poly(-2*x + 1, x, domain='ZZ')"
    assert str(Poly(-2*x - 1, x)) == "Poly(-2*x - 1, x, domain='ZZ')"

    assert str(Poly(x - 1, x)) == "Poly(x - 1, x, domain='ZZ')"

    assert str(Poly(x**2 + 1 + y, x)) == "Poly(x**2 + y + 1, x, domain='ZZ[y]')"
    assert str(Poly(x**2 - 1 + y, x)) == "Poly(x**2 + y - 1, x, domain='ZZ[y]')"

    assert str(Poly(x**2 + I*x, x)) == "Poly(x**2 + I*x, x, domain='EX')"
    assert str(Poly(x**2 - I*x, x)) == "Poly(x**2 - I*x, x, domain='EX')"

    assert str(Poly(-x*y*z + x*y - 1, x, y, z)) == "Poly(-x*y*z + x*y - 1, x, y, z, domain='ZZ')"
    assert str(Poly(-w*x**21*y**7*z + (1 + w)*z**3 - 2*x*z + 1, x, y, z)) == \
        "Poly(-w*x**21*y**7*z - 2*x*z + (w + 1)*z**3 + 1, x, y, z, domain='ZZ[w]')"

    assert str(Poly(x**2 + 1, x, modulus=2)) == "Poly(x**2 + 1, x, modulus=2)"
    assert str(Poly(2*x**2 + 3*x + 4, x, modulus=17)) == "Poly(2*x**2 + 3*x + 4, x, modulus=17)"

def test_Pow():
    assert str(x**-1) == "1/x"
    assert str(x**-2) == "x**(-2)"
    assert str(x**2) == "x**2"
    assert str((x+y)**-1) == "1/(x + y)"
    assert str((x+y)**-2) == "(x + y)**(-2)"
    assert str((x+y)**2) == "(x + y)**2"
    assert str((x+y)**(1+x)) == "(x + y)**(x + 1)"
    assert str(x**Rational(1, 3)) == "x**(1/3)"
    assert str(1/x**Rational(1, 3)) == "x**(-1/3)"
    assert str(sqrt(sqrt(x))) == "x**(1/4)"

def test_sqrt():
    assert str(sqrt(x)) == "sqrt(x)"
    assert str(sqrt(x**2)) == "sqrt(x**2)"
    assert str(1/sqrt(x)) == "1/sqrt(x)"
    assert str(1/sqrt(x**2)) == "1/sqrt(x**2)"
    assert str(y/sqrt(x)) == "y/sqrt(x)"
    assert str(x**(1/2)) == "x**0.5"
    assert str(1/x**(1/2)) == "x**-0.5"

def test_Rational():
    n1 = Rational(1,4)
    n2 = Rational(1,3)
    n3 = Rational(2,4)
    n4 = Rational(2,-4)
    n5 = Rational(0)
    n6 = Rational(1)
    n7 = Rational(3)
    n8 = Rational(-3)
    assert str(n1*n2) == "1/12"
    assert str(n1*n2) == "1/12"
    assert str(n3) == "1/2"
    assert str(n1*n3) == "1/8"
    assert str(n1+n3) == "3/4"
    assert str(n1+n2) == "7/12"
    assert str(n1+n4) == "-1/4"
    assert str(n4*n4) == "1/4"
    assert str(n4+n2) == "-1/6"
    assert str(n4+n5) == "-1/2"
    assert str(n4*n5) == "0"
    assert str(n3+n4) == "0"
    assert str(n1**n7) == "1/64"
    assert str(n2**n7) == "1/27"
    assert str(n2**n8) == "27"
    assert str(n7**n8) == "1/27"
    assert str(Rational("-25")) == "-25"
    assert str(Rational("1.25")) == "5/4"
    assert str(Rational("-2.6e-2")) == "-13/500"
    assert str(S("25/7")) == "25/7"
    assert str(S("-123/569")) == "-123/569"
    assert str(S("0.1[23]", rational=1)) == "61/495"
    assert str(S("5.1[666]", rational=1)) == "31/6"
    assert str(S("-5.1[666]", rational=1)) == "-31/6"
    assert str(S("0.[9]", rational=1)) == "1"
    assert str(S("-0.[9]", rational=1)) == "-1"

    assert str(sqrt(Rational(1,4))) == "1/2"
    assert str(sqrt(Rational(1,36))) == "1/6"

    assert str((123**25) ** Rational(1,25)) == "123"
    assert str((123**25+1)**Rational(1,25)) != "123"
    assert str((123**25-1)**Rational(1,25)) != "123"
    assert str((123**25-1)**Rational(1,25)) != "122"

    assert str(sqrt(Rational(81,36))**3) == "27/8"
    assert str(1/sqrt(Rational(81,36))**3) == "8/27"

    assert str(sqrt(-4)) == str(2*I)
    assert str(2**Rational(1,10**10)) == "2**(1/10000000000)"

def test_Float():
    # NOTE prec is the whole number of decimal digits
    assert str(Float('1.23', prec=1+2))    == '1.23'
    assert str(Float('1.23456789', prec=1+8))  == '1.23456789'
    assert str(Float('1.234567890123456789', prec=1+18))    == '1.234567890123456789'
    assert str(pi.evalf(1+2))   == '3.14'
    assert str(pi.evalf(1+14))  == '3.14159265358979'
    assert str(pi.evalf(1+64))  == '3.1415926535897932384626433832795028841971693993751058209749445923'

def test_Relational():
    assert str(Rel(x, y, "<")) == "x < y"
    assert str(Rel(x+y, y, "==")) == "x + y == y"

def test_RootOf():
    assert str(RootOf(x**5 + 2*x - 1, 0)) == "RootOf(x**5 + 2*x - 1, 0)"

def test_RootSum():
    f = x**5 + 2*x - 1

    assert str(RootSum(f, Lambda(z, z), auto=False)) == "RootSum(x**5 + 2*x - 1)"
    assert str(RootSum(f, Lambda(z, z**2), auto=False)) == "RootSum(x**5 + 2*x - 1, Lambda(_z, _z**2))"

def test_GroebnerBasis():
    assert str(groebner([], x, y)) == "GroebnerBasis([], x, y, domain='ZZ', order='lex')"

    F = [x**2 - 3*y - x + 1, y**2 - 2*x + y - 1]

    assert str(groebner(F, order='grlex')) == \
        "GroebnerBasis([x**2 - x - 3*y + 1, y**2 - 2*x + y - 1], x, y, domain='ZZ', order='grlex')"
    assert str(groebner(F, order='lex')) == \
        "GroebnerBasis([2*x - y**2 - y + 1, y**4 + 2*y**3 - 3*y**2 - 16*y + 7], x, y, domain='ZZ', order='lex')"

def test_Sample():
    assert str(Sample([x, y, 1])) in [
            "Sample([x, y, 1])",
            "Sample([y, 1, x])",
            "Sample([1, x, y])",
            "Sample([y, x, 1])",
            "Sample([x, 1, y])",
            "Sample([1, y, x])",
            ]

def test_set():
    assert sstr(set())       == 'set()'
    assert sstr(frozenset()) == 'frozenset()'

    assert sstr(set([1,2,3]))== 'set([1, 2, 3])'
    assert sstr(set([1,x,x**2,x**3,x**4]))   == 'set([1, x, x**2, x**3, x**4])'

def test_SparseMatrix():
    M = SparseMatrix([[x**+1, 1], [y, x+y]])
    assert str(M) == sstr(M) == "[x,     1]\n[y, x + y]"

def test_Sum():
    assert str(summation(cos(3*z), (z, x, y))) == "Sum(cos(3*z), (z, x, y))"
    assert str(Sum(x*y**2, (x, -2, 2), (y, -5, 5))) == \
        "Sum(x*y**2, (x, -2, 2), (y, -5, 5))"

def test_Symbol():
    assert str(y) == "y"
    assert str(x) == "x"
    e = x
    assert str(e) == "x"

def test_tuple():
    assert str((x,)) == sstr((x,)) == "(x,)"
    assert str((x+y, 1+x)) == sstr((x+y, 1+x)) == "(x + y, x + 1)"
    assert str((x+y, (1+x, x**2))) == sstr((x+y, (1+x, x**2))) == "(x + y, (x + 1, x**2))"

def test_Uniform():
    assert str(Uniform(x, y)) == "Uniform(x, y)"
    assert str(Uniform(x+y, y)) == "Uniform(x + y, y)"

def test_Unit():
    assert str(second) == "s"
    assert str(joule) == "kg*m**2/s**2" # issue 2461

def test_wild_str():
    # Check expressions containing Wild not causing infinite recursion
    w = Wild('x')
    assert str(w + 1)           == 'x_ + 1'
    assert str(exp(2**w) + 5)   == 'exp(2**x_) + 5'
    assert str(3*w + 1)         == '3*x_ + 1'
    assert str(1/w + 1)         == '1 + 1/x_'
    assert str(w**2 + 1)        == 'x_**2 + 1'
    assert str(1/(1-w))         == '1/(-x_ + 1)'

def test_zeta():
    assert str(zeta(3)) == "zeta(3)"

def test_bug2():
    e = x-y
    a = str(e)
    b = str(e)
    assert a == b


def test_bug4():
    e = -2*sqrt(x)-y/sqrt(x)/2
    assert str(e) not in ["(-2)*x**1/2(-1/2)*x**(-1/2)*y",
            "-2*x**1/2(-1/2)*x**(-1/2)*y","-2*x**1/2-1/2*x**-1/2*w"]
    assert str(e) == "-2*sqrt(x) - y/(2*sqrt(x))"

def test_issue922():
    e = Integral(x,x) + 1
    assert str(e)   == 'Integral(x, x) + 1'

def test_sstrrepr():
    assert sstr('abc')      == 'abc'
    assert sstrrepr('abc')  == "'abc'"

    e = ['a', 'b', 'c', x]
    assert sstr(e)      == "[a, b, c, x]"
    assert sstrrepr(e)  == "['a', 'b', 'c', x]"

def test_infinity():
    assert sstr(I*oo) == "oo*I"

def test_full_prec():
    assert sstr(S("0.3"), full_prec=True) == "0.300000000000000"
    assert sstr(S("0.3"), full_prec="auto") == "0.300000000000000"
    assert sstr(S("0.3"), full_prec=False) == "0.3"
    assert sstr(S("0.3")*x, full_prec=True) in [
            "0.300000000000000*x",
            "x*0.300000000000000"
            ]
    assert sstr(S("0.3")*x, full_prec="auto") in [
            "0.3*x",
            "x*0.3"
            ]
    assert sstr(S("0.3")*x, full_prec=False) in [
            "0.3*x",
            "x*0.3"
            ]

def test_noncommutative():
    A, B, C = symbols('A,B,C', commutative=False)

    assert sstr(A*B*C**-1) == "A*B*C**(-1)"
    assert sstr(C**-1*A*B) == "C**(-1)*A*B"
    assert sstr(A*C**-1*B) == "A*C**(-1)*B"
    assert sstr(sqrt(A)) == "sqrt(A)"
    assert sstr(1/sqrt(A)) == "A**(-1/2)"

def test_empty_printer():
    str_printer = StrPrinter()
    assert str_printer.emptyPrinter("foo") == "foo"
    assert str_printer.emptyPrinter(x*y) == "x*y"
    assert str_printer.emptyPrinter(32) == "32"

def test_settings():
    raises(TypeError, 'sstr(S(4), method="garbage")')
