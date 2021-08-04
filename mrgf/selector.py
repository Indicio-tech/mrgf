"""Selector used to route principals to appropriate handlers for their privileges."""

from asyncio import iscoroutinefunction
from functools import wraps
from typing import Awaitable, Callable, Dict, Union, cast

from .governance_framework import Principal


PrincipalFinder = Callable[..., Union[Principal, dict]]
AsyncPrincipalFinder = Callable[..., Awaitable[Union[Principal, dict]]]
Condition = Callable[[Principal], bool]


def _asyncify(func) -> AsyncPrincipalFinder:
    """Wrap method in asynchronous method for homogeneity."""

    if iscoroutinefunction(func):
        return func
    else:

        async def _asyncified_function(*args, **kwargs):
            return func(*args, **kwargs)

        return _asyncified_function


def _ensure_principal(value: Union[Principal, dict]) -> Principal:
    """Parse dict as principal or return principal."""
    if isinstance(value, Principal):
        return value
    if isinstance(value, dict):
        return Principal(**value)

    raise TypeError(
        "Invalid principal; expected dict or Principal, received {}".format(
            type(value).__name__
        )
    )


class Selector:
    """Enacts and enforces rules that govern execution flow."""

    def __init__(self, principal_finder: Union[PrincipalFinder, AsyncPrincipalFinder]):
        """Initialize Enforcer."""
        self._principal_finder = principal_finder
        self._finder_async = iscoroutinefunction(principal_finder)
        self._governed = []

    def select(self, func: Callable):
        """Decorate a function or method as requiring privileges."""
        is_async = iscoroutinefunction(func)
        if self._finder_async and not is_async:
            raise TypeError(
                "Handler must be asynchronous when principal finder is asynchronous"
            )

        alternatives: Dict[Callable, Callable] = {}

        def register(condition: Callable[[Principal], bool]):
            def _register(func: Callable):
                if not is_async and iscoroutinefunction(func):
                    raise TypeError(
                        "Default handler is not async; "
                        "registred handler must also be synchronous"
                    )
                alternatives[condition] = _asyncify(func) if is_async else func

                return func

            return _register

        if is_async:
            async_principal_finder = _asyncify(self._principal_finder)

            @wraps(func)
            async def _async_wrapper(*args, **kwargs):
                """Check the rules and allow principal in if conditions met."""
                principal = _ensure_principal(
                    await async_principal_finder(*args, **kwargs)
                )

                for condition, alternative in alternatives.items():
                    if condition(principal):
                        return await alternative(*args, **kwargs)
                return await func(*args, **kwargs)

            wrapper = _async_wrapper
        else:
            principal_finder = cast(PrincipalFinder, self._principal_finder)

            @wraps(func)
            def _wrapper(*args, **kwargs):
                """Check the rules and allow principal in if conditions met."""
                principal = _ensure_principal(principal_finder(*args, **kwargs))
                for condition, alternative in alternatives.items():
                    if condition(principal):
                        return alternative(*args, **kwargs)
                return func(*args, **kwargs)

            wrapper = _wrapper

        self._governed.append(func)
        wrapper.register = register
        wrapper.alternatives = alternatives
        return wrapper
