"""Test mrgf.decorators."""

from typing import Awaitable, Callable

import pytest

from mrgf.selector import PrincipalSelector, select


def test_select():
    selected = select(
        (lambda: False, ["first"]),
        (lambda: True, ["second"]),
        default=["test"],
    )()
    assert selected == ["second"]

    selector = select(
        (lambda a: a is True, "a"), (lambda b: b is False, "b"), default="c"
    )
    assert selector(True) == "a"
    assert selector(False) == "b"
    assert selector("asdf") == "c"

    def complex_condition(a: int):
        return a == 10

    selector = select((complex_condition, "complex_condition"), default="default")
    assert selector(10) == "complex_condition"
    assert selector(1) == "default"


@pytest.mark.asyncio
async def test_async_selector():
    """Test basic function of the selector."""

    selector = PrincipalSelector(Callable[[str], Awaitable[str]])

    @selector.default
    async def operation(arg1):
        print("From default", arg1)
        return "default"

    @selector.register(lambda p: "test" in p.roles)
    async def alternative(arg1):
        print("From alternative", arg1)
        return "alternative"

    assert await selector({"roles": "test"})("test") == "alternative"
    assert await selector({"roles": "asdf"})("test") == "default"


def test_sync_selector():
    """Test basic function of the selector."""

    selector = PrincipalSelector(Callable[[str], str])

    @selector.default
    def operation(arg1: str):
        print("From default", arg1)
        return "default"

    @selector.register(lambda p: "test" in p.roles)
    def alternative(arg1):
        print("From alternative", arg1)
        return "alternative"

    @selector.register(lambda p: "test" in p.roles)
    def alternative1(arg1):
        print("From alternative 1", arg1)
        return "alternative1"

    assert selector({"roles": "test"})("test") == "alternative"
    assert selector({"roles": "asdf"})("asdf") == "default"


def test_selector_register():
    selector = PrincipalSelector()

    @selector.register(lambda p: "test" in p.roles)
    def opt1(arg1: str):
        return arg1

    assert selector({"roles": "test"})("test")
