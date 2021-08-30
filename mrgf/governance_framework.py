"""Data structures for holding governance frameworks."""

from typing import Any, Dict, List, Optional, Set, Union
from pydantic import BaseModel, Extra, Field, validator
from pydantic.class_validators import root_validator
from typing_extensions import Annotated

from sgl.api import satisfies


class JsonLDDocument(BaseModel):
    context: Annotated[List[Union[str, dict]], Field(alias="@context")]

    @validator("context", pre=True)
    @classmethod
    def _ensure_list(cls, value: Any):
        """Normalize @context to list."""
        if not isinstance(value, list):
            return [value]
        return value


class NamedObject(BaseModel):
    class Config:
        extra = Extra.allow

    name: str

    @property
    def extra(self) -> Dict[str, Any]:
        """Return a dictionary with access to values from extra properties."""
        return self.__dict__


class Definition(NamedObject):
    id: str


class Privilege(NamedObject):
    uri: str


class Duty(Privilege):
    pass


class Condition(BaseModel):
    class Config:
        extra = Extra.allow

    n: Optional[int] = None
    roles: Optional[str] = None
    # "op" is listed in docs but not actually supported
    # op: Optional[str] = None
    any: Optional[List["Condition"]] = None
    all: Optional[List["Condition"]] = None


# Required for self-references in "any" and "all"
Condition.update_forward_refs()


class Rule(BaseModel):
    class Config:
        extra = Extra.allow

    id: Optional[str] = None
    grant: List[str]
    when: Condition
    thus: Optional[str] = None
    duties: Optional[List[str]] = None


class Principal(BaseModel):
    """Subject about which rules are tested."""

    class Config:
        extra = Extra.allow

    id: Optional[str] = None
    roles: Set[str] = set()
    privileges: Set[str] = set()

    @root_validator(pre=True)
    @classmethod
    def _id_or_roles_present(cls, values):
        if "id" not in values and "roles" not in values:
            raise ValueError("either id or roles must have a meaningful value")
        return values

    @validator("roles", "privileges", pre=True)
    @classmethod
    def _transform_singular_to_set(cls, value):
        if isinstance(value, str):
            return {value}
        return value

    @validator("roles", "privileges", pre=True)
    @classmethod
    def _transform_list_to_set(cls, value):
        if isinstance(value, list):
            return set(value)
        return value


class GovernanceFramework(JsonLDDocument):
    """Data structure for holding governance frameworks."""

    class Config:
        extra = Extra.allow
        underscore_attrs_are_private = True

    # Required
    name: str
    version: str
    data_uri: str

    # Governance
    roles: Optional[List[str]] = None
    define: Optional[List[Definition]] = None
    rules: List[Rule] = []
    privileges: Optional[List[Privilege]]
    duties: Optional[List[Duty]]

    # Metadata
    docs_uri: Optional[str] = None
    topics: Optional[List[str]] = None
    jurisdictions: Optional[List[str]] = None
    geos: Optional[List[str]]
    logo: Optional[str] = None
    description: Optional[str] = None

    _privilege_map: Optional[Dict[str, Privilege]] = None

    def privilege(self, name: str):
        """Retrieve a specific privilege by name."""
        if self._privilege_map is None:
            self._privilege_map = (
                {priv.name: priv for priv in self.privileges} if self.privileges else {}
            )
        return self._privilege_map[name]

    def evaluate(self, principal: Principal) -> Set[str]:
        """Evaluate rules on principal and return set of granted privileges."""
        privileges = set()
        size_on_previous_iteration = -1
        while size_on_previous_iteration < len(privileges):
            size_on_previous_iteration = len(privileges)
            for rule in self.rules:
                if satisfies(principal.dict(), rule.dict()):
                    privileges.update(rule.grant)
        return privileges

    def update(self, other: "GovernanceFramework"):
        """Update this framework with another.

        This follows dictionary update semantics.
        """
        self.__dict__.update(other.__dict__)
