"""Test mrgf.decorators."""

import pytest
from mrgf import Selector


@pytest.mark.asyncio
async def test_async_selector():
    """Test basic function of the enforcer."""

    async def _finder(arg1):
        return {"roles": arg1}

    enforcer = Selector(_finder)

    @enforcer.select
    async def operation(arg1):
        print("From default", arg1)
        return "default"

    @operation.register(lambda p: "test" in p.roles)
    async def alternative(arg1):
        print("From alternative", arg1)
        return "alternative"

    assert await operation("test") == "alternative"
    assert await operation("asdf") == "default"


def test_sync_selector():
    """Test basic function of the enforcer."""

    def _finder(arg1):
        return {"roles": arg1}

    enforcer = Selector(_finder)

    @enforcer.select
    def operation(arg1):
        print("From default", arg1)
        return "default"

    @operation.register(lambda p: "test" in p.roles)
    def alternative(arg1):
        print("From alternative", arg1)
        return "alternative"

    assert operation("test") == "alternative"
    assert operation("asdf") == "default"
