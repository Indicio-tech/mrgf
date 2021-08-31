"""Selector used to route principals to appropriate handlers for their privileges."""

from typing import (
    Callable,
    Dict,
    Generic,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
)
from typing_extensions import ParamSpec

from .governance_framework import Principal


class NoOptionSelected(Exception):
    """Raised when no option was selected and no default available."""


Selected = TypeVar("Selected")
ConditionParams = ParamSpec("ConditionParams")


def select(
    *options: Tuple[Callable[ConditionParams, bool], Selected],
    default: Optional[Selected] = None,
) -> Callable[ConditionParams, Selected]:
    """Return one option based on a set of callables."""

    def _select(
        *args: ConditionParams.args, **kwargs: ConditionParams.kwargs
    ) -> Selected:
        for condition, alternative in options:
            if condition(*args, **kwargs):
                return alternative
        if default:
            return default
        raise NoOptionSelected("No option selected and no default provided.")

    return _select


class Selector(Generic[Selected]):
    """Enacts and enforces rules that govern execution flow."""

    def __init__(self, selected: Optional[Type[Selected]] = None):
        """Initialize Enforcer."""
        self._options: Dict[Callable[..., bool], Selected] = {}
        self._default: Optional[Selected] = None

    def register(self, condition: Callable[..., bool]):
        def _register(func: Selected):
            self._options[condition] = func
            return func

        return _register

    def default(self, func: Selected):
        if self._default:
            raise TypeError("Default is already set on selector.")
        self._default = func
        return func

    @property
    def registered(self):
        return self._options

    def __call__(self, *args, **kwargs) -> Selected:
        return select(*self._options.items(), default=self._default)(*args, **kwargs)


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


class PrincipalSelector(Selector[Selected]):
    """Enacts and enforces rules that govern execution flow."""

    def __init__(self, selected: Optional[Type[Selected]] = None):
        """Initialize Enforcer."""
        self._options: Dict[Callable[[Principal], bool], Selected] = {}
        self._default: Optional[Selected] = None

    def register(self, condition: Callable[[Principal], bool]):
        def _register(func: Selected):
            self._options[condition] = func
            return func

        return _register

    def __call__(self, principal: Union[Principal, dict]) -> Selected:
        return select(*self._options.items(), default=self._default)(
            _ensure_principal(principal)
        )
