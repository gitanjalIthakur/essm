# -*- coding: utf-8 -*-

"""Core equation type."""

from __future__ import absolute_import

from sage.misc.latex import latex

from ..variables import SHORT_UNIT_SYMBOLS, Variable


def convert(expr):
    op = expr.operator()
    ops = expr.operands()
    if op:
        if len(ops) == 2:
            return op(*map(convert, ops))
        return op(convert(ops[0]), reduce(op, map(convert, ops[1:])))
    return expr.convert() if hasattr(expr, 'convert') else expr


def markdown(unit):
    """Return markdown representaion of a unit."""
    #FIXME consider (m/s)**(s/2)
    facs = unit.factor_list()
    str1 = ''
    for term1 in facs:
        op1 = term1[1]
        if op1 == 1:
            str1 = str(term1[0]) + ' ' + str1
        else:
            str1 += ' {0}$^{{{1}}}$ '.format(markdown(term1[0]), markdown(op1))
    return str1


class EquationMeta(type):
    """Equation interface."""

    def __new__(cls, name, parents, dct):
        """Build and register new variable."""
        if '__registry__' not in dct:
            name = dct.get('name', name)

        return super(EquationMeta, cls).__new__(cls, name, parents, dct)

    def __init__(cls, name, bases, dct):
        """Register variable."""
        if '__registry__' not in dct:
            expanded_units = cls.expand_units()
            if not expanded_units:
                raise ValueError(
                    'Invalid expression units: {0}'.format(expanded_units)
                )
            cls.__registry__[name] = cls
            cls.__expressions__[cls.expr] = cls


class Equation(object):
    """Base type for all equation."""
    __metaclass__ = EquationMeta
    __registry__ = {}
    __expressions__ = {}
    __defaults__ = {}

    @classmethod
    def from_expression(cls, expr):
        """Return class for given expression."""
        return cls.__expressions__[expr]

    @classmethod
    def expand_units(cls, simplify_full=True):
        """Expand units of all arguments in expression."""
        used_units = {}
        # Need to multiply units with variable,
        # so that we can devide by the symbolic equation later:
        for variable in cls.expr.arguments():
            used_units[variable] = variable * Variable.__units__[variable]

        result = convert(cls.expr.subs(used_units)/cls.expr)
        if simplify_full:
            result = result.simplify_full()
        return result

    @classmethod
    def short_unit(cls):
        """Return short unit representation."""
        return cls.expand_units().lhs().subs(SHORT_UNIT_SYMBOLS)


def register(cls):
    """Register symbolic variable instead of class definition."""
    return cls.expr


__all__ = (
    'Equation',
    'convert',
    'register',
)
