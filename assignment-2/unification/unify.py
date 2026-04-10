from convCNF import *
import sys

def unify(A, B, bindings):
    return unify1(A, B, 0, bindings)

def unify1(A, B, pos, bindings):
    if bindings is None:
        return None

    if A.toString() == B.toString():
        return bindings

    if isVar(A):
        return unifyVar(A.atom, B, bindings)

    if isVar(B):
        return unifyVar(B.atom, A, bindings)

    if isConst(A) or isConst(B):
        return None

    if len(A.list) != len(B.list):
        return None

    if pos == len(A.list):
        return bindings

    updated = unify(A.list[pos], B.list[pos], bindings)
    if updated is None:
        return None

    return unify1(A, B, pos + 1, updated)

def unifyVar(var, expr, bindings):
    if var in bindings:
        return unify(bindings[var], expr, bindings)

    if isVar(expr) and expr.atom in bindings:
        varExpr = Sexpr(tokenize(var), 0)
        return unify(varExpr, bindings[expr.atom], bindings)

    bindings[var] = expr
    return bindings

def subst(bindings, expr):
    if isVar(expr):
        if expr.atom in bindings:
            return subst(bindings, bindings[expr.atom])

    if expr.atom is not None:
        return expr

    temp = expr.copy()
    temp.list = [subst(bindings, x) for x in temp.list]
    return temp

A = sys.argv[1]
B = sys.argv[2]

A = Sexpr(tokenize(A), 0)
B = Sexpr(tokenize(B), 0)

unifier = unify(A, B, {})

if unifier is None:
    print("not unifiable")
else:
    for var, expr in unifier.items():
        print(f"{var} -> {expr.toString()}")
    print(f"{subst(unifier, A).toString()} = {subst(unifier, B).toString()}")