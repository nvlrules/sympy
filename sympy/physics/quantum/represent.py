"""Logic for representing operators in state in various bases.

TODO:
* Get represent working with continuous hilbert spaces.
* Document default basis functionality.
"""

from sympy import Add, Mul, Pow, I, Expr
from sympy.functions import conjugate

from sympy.physics.quantum.dagger import Dagger
from sympy.physics.quantum.commutator import Commutator
from sympy.physics.quantum.anticommutator import AntiCommutator
from sympy.physics.quantum.innerproduct import InnerProduct
from sympy.physics.quantum.qexpr import QExpr
from sympy.physics.quantum.tensorproduct import TensorProduct
from sympy.physics.quantum.matrixutils import flatten_scalar
from sympy.physics.quantum.state import KetBase, BraBase
from sympy.physics.quantum.operator import Operator
from sympy.physics.quantum.qapply import qapply

__all__ = [
    'represent'
]

#-----------------------------------------------------------------------------
# Represent
#-----------------------------------------------------------------------------

def _sympy_to_scalar(e):
    """Convert from a sympy scalar to a Python scalar."""
    if isinstance(e, Expr):
        if e.is_Integer:
            return int(e)
        elif e.is_Float:
            return float(e)
        elif e.is_Rational:
            return float(e)
        elif e.is_Number or e.is_NumberSymbol or e == I:
            return complex(e)
    raise TypeError('Expected number, got: %r' % e)


def represent(expr, **options):
    """Represent the quantum expression in the given basis.

    In quantum mechanics abstract states and operators can be represented in
    various basis sets. Under this operation the follow transforms happen:

    * Ket -> column vector or function
    * Bra -> row vector of function
    * Operator -> matrix or differential operator

    This function is the top-level interface for this action.

    This function walks the sympy expression tree looking for ``QExpr``
    instances that have a ``_represent`` method. This method is then called
    and the object is replaced by the representation returned by this method.
    By default, the ``_represent`` method will dispatch to other methods
    that handle the representation logic for a particular basis set. The
    naming convention for these methods is the following::

        def _represent_FooBasis(self, e, basis, **options)

    This function will have the logic for representing instances of its class
    in the basis set having a class named ``FooBasis``.

    Parameters
    ==========
    expr  : Expr
        The expression to represent.
    basis : Operator, basis set
        An object that contains the information about the basis set. If an
        operator is used, the basis is assumed to be the orthonormal
        eigenvectors of that operator. In general though, the basis argument
        can be any object that contains the basis set information.
    options : dict
        Key/value pairs of options that are passed to the underlying method
        that does finds the representation. These options can be used to
        control how the representation is done. For example, this is where
        the size of the basis set would be set.

    Returns
    =======
    e : Expr
        The sympy expression of the represented quantum expression.

    Examples
    ========

    Here we subclass ``Operator`` and ``Ket`` to create the z-spin operator
    and its spin 1/2 up eigenstate. By definining the ``_represent_SzOp``
    method, the ket can be represented in the z-spin basis.

        >>> from sympy.physics.quantum import Operator, represent, Ket
        >>> from sympy import Matrix

        >>> class SzUpKet(Ket):
        ...     def _represent_SzOp(self, basis, **options):
        ...         return Matrix([1,0])
        ...
        >>> class SzOp(Operator):
        ...     pass
        ...
        >>> sz = SzOp('Sz')
        >>> up = SzUpKet('up')
        >>> represent(up, basis=sz)
        [1]
        [0]
    """
    format = options.get('format', 'sympy')
    if isinstance(expr, QExpr):
        try:
            return expr._represent(**options)
        except NotImplementedError as strerr:
            if isinstance(expr, (KetBase, BraBase)):
                try:
                    return rep_innerproduct(expr, **options)
                except NotImplementedError:
                    raise NotImplementedError(strerr)
            elif isinstance(expr, Operator):
                try:
                    return rep_expectation(expr, **options)
                except NotImplementedError:
                    raise NotImplementedError(strerr)
            else:
                raise NotImplementedError(strerr)
    elif isinstance(expr, Add):
        result = represent(expr.args[0], **options)
        for args in expr.args[1:]:
            # scipy.sparse doesn't support += so we use plain = here.
            result = result + represent(args, **options)
        return result
    elif isinstance(expr, Pow):
        exp = expr.exp
        if format == 'numpy' or format == 'scipy.sparse':
            exp = _sympy_to_scalar(exp)
        return represent(expr.base, **options)**exp
    elif isinstance(expr, TensorProduct):
        new_args = [represent(arg, **options) for arg in expr.args]
        return TensorProduct(*new_args)
    elif isinstance(expr, Dagger):
        return Dagger(represent(expr.args[0], **options))
    elif isinstance(expr, Commutator):
        A = represent(expr.args[0], **options)
        B = represent(expr.args[1], **options)
        return A*B - B*A
    elif isinstance(expr, AntiCommutator):
        A = represent(expr.args[0], **options)
        B = represent(expr.args[1], **options)
        return A*B + B*A
    elif isinstance(expr, InnerProduct):
        return represent(Mul(expr.bra,expr.ket), **options)
    elif not isinstance(expr, Mul):
        # For numpy and scipy.sparse, we can only handle numerical prefactors.
        if format == 'numpy' or format == 'scipy.sparse':
            return _sympy_to_scalar(expr)
        return expr

    if not isinstance(expr, Mul):
        raise TypeError('Mul expected, got: %r' % expr)

    if options.has_key("index"):
        options["index"] += 1
    else:
        options["index"] = 1

    result = represent(expr.args[-1], **options)
    last_arg = expr.args[-1]

    for arg in reversed(expr.args[:-1]):
        if isinstance(last_arg, Operator):
            options["index"] += 1
        elif isinstance(last_arg, BraBase) and isinstance(arg, KetBase):
            options["index"] += 1

        result = represent(arg, **options)*result

    #TODO: Collapse DiracDelta functions

    # All three matrix formats create 1 by 1 matrices when inner products of
    # vectors are taken. In these cases, we simply return a scalar.
    result = flatten_scalar(result)
    return result

def rep_innerproduct(expr, **options):
    """ Attempts to calculate inner product with a bra from the specified basis and if this fails
        resorts to the standard represent specified in QExpr; Should only be passed an instance
        of KetBase or BraBase"""

    if not isinstance(expr, (KetBase, BraBase)):
        raise TypeError("expr passed is not a Bra or Ket")

    basis = options.pop('basis', None)

    #If the basis is not specified, try to find the default basis to form an inner product with
    if basis is None and expr.basis_op() is None:
        raise NotImplementedError("Could not get basis set for operator")
    elif basis is None:
        basis = (expr.basis_op())()

    if not options.has_key("index"):
        options["index"] = 1

    #Once we know the basis, try to get the basis kets and form an inner product
    if basis.basis_set is not None:
        basis_kets = basis._get_basis_kets(options["index"], 2)

        if isinstance(expr, BraBase):
            bra = expr
            ket =  (basis_kets[1] if basis_kets[0].dual == expr else basis_kets[0])
        else:
            bra = (basis_kets[1].dual if basis_kets[0] == expr else basis_kets[0].dual)
            ket = expr

        prod = InnerProduct(bra, ket)
        result = prod.doit()

        format = options.get('format', 'sympy')
        return expr._format_represent(result, format)
    else:
        raise NotImplementedError("Could not get basis set for operator")

def rep_expectation(expr, **options):
    """Attempts to form an expectation value like expression for representing an operator.

    Returns the result of evaluating something of the form <x'|A|x>"""

    basis = options.pop('basis', None)

    if not options.has_key("index"):
        options["index"] = 1

    if not isinstance(expr, Operator):
        raise TypeError("The passed expression is not an operator")

    if basis is None and expr.basis_ket() is None:
        raise NotImplementedError("Could not get basis kets for this operator")
    elif basis is None:
        basis_kets = expr._get_basis_kets(options["index"], 2)

    bra = basis_kets[1].dual
    ket = basis_kets[0]

    return qapply(bra*expr*ket)
