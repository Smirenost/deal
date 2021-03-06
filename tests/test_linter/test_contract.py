# built-in
import ast
from textwrap import dedent

# external
import astroid

# project
from deal.linter._contract import Category, Contract
from deal.linter._func import Func


TEXT = """
import deal

@deal.raises(ValueError, UnknownError, idk_what_is_it())
@notadeal.raises(KeyError)
def f(x):
    return x
"""


def test_exceptions():
    funcs1 = Func.from_ast(ast.parse(TEXT))
    assert len(funcs1) == 1
    funcs2 = Func.from_astroid(astroid.parse(TEXT))
    assert len(funcs2) == 1
    for func in (funcs1[0], funcs2[0]):
        assert len(func.contracts) == 1
        contract = func.contracts[0]
        assert contract.exceptions == [ValueError, 'UnknownError']


def test_repr():
    c = Contract(category=Category.RAISES, args=[], func_args=None)
    assert repr(c) == 'Contract(raises)'


def test_run():
    text = """
    import deal

    @deal.post(lambda x: x > 0)
    def f(x):
        return x
    """
    text = dedent(text).strip()
    funcs1 = Func.from_ast(ast.parse(text))
    assert len(funcs1) == 1
    funcs2 = Func.from_astroid(astroid.parse(text))
    assert len(funcs2) == 1
    for func in (funcs1[0], funcs2[0]):
        assert len(func.contracts) == 1
        c = func.contracts[0]
        assert c.run(1) is True
        assert c.run(-1) is False


def test_resolve_func():
    text = """
    import deal

    def contract(x):
        return x > 0

    @deal.post(contract)
    def f(x):
        ...
    """
    text = dedent(text).strip()
    funcs = Func.from_astroid(astroid.parse(text))
    assert len(funcs) == 2
    func = funcs[-1]
    assert len(func.contracts) == 1
    c = func.contracts[0]
    assert c.run(1) is True
    assert c.run(-1) is False


def test_resolve_lambda():
    text = """
    import deal

    contract = lambda x: x > 0

    @deal.post(contract)
    def f(x):
        ...
    """
    text = dedent(text).strip()
    funcs = Func.from_astroid(astroid.parse(text))
    assert len(funcs) == 1
    func = funcs[0]
    assert len(func.contracts) == 1
    c = func.contracts[0]
    assert c.run(1) is True
    assert c.run(-1) is False


def test_return_message():
    text = """
    import deal

    @deal.post(lambda x: x > 0 or 'oh no!')
    def f(x):
        return x
    """
    text = dedent(text).strip()
    funcs1 = Func.from_ast(ast.parse(text))
    assert len(funcs1) == 1
    funcs2 = Func.from_astroid(astroid.parse(text))
    assert len(funcs2) == 1
    for func in (funcs1[0], funcs2[0]):
        assert len(func.contracts) == 1
        c = func.contracts[0]
        assert c.run(1) is True
        assert c.run(-1) == 'oh no!'


def test_simplified_signature():
    text = """
    import deal

    @deal.post(lambda _: _.a > _.b)
    def f(a, b):
        return a + b
    """
    text = dedent(text).strip()
    funcs1 = Func.from_ast(ast.parse(text))
    assert len(funcs1) == 1
    funcs2 = Func.from_astroid(astroid.parse(text))
    assert len(funcs2) == 1
    for func in (funcs1[0], funcs2[0]):
        assert len(func.contracts) == 1
        c = func.contracts[0]
        assert c.run(3, 2) is True
        assert c.run(2, 3) is False
