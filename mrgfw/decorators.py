"""Decorators for use with Machine Readable Governance Frameworks and handlers."""

from typing import Callable, Optional, Sequence, Union
from typing_extensions import Protocol

from .models import Principle


class PrincipleFinder(Protocol):
    """Returns the principle as derived from arguments."""

    def __call__(self, *args, **kwargs) -> Union[Principle, dict]:
        ...


def privilege(
    privileges: Sequence[str], principle: Optional[PrincipleFinder]
) -> Callable:
    """Require privilege on principle."""
    pass
