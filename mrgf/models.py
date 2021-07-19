"""Data structures for holding governance frameworks."""

from typing import Any, List, Optional, Set, Union
from pydantic import BaseModel, Extra, Field, validator
from pydantic.class_validators import root_validator
from typing_extensions import Annotated


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
    op: Optional[str] = None
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


class GovernaceFramework(JsonLDDocument):
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
    rules: Optional[List[Rule]] = None
    privileges: Optional[List[Privilege]]
    duties: Optional[List[Duty]]

    # Metadata
    docs_uri: Optional[str] = None
    topics: Optional[List[str]] = None
    jurisdictions: Optional[List[str]] = None
    geos: Optional[List[str]]
    logo: Optional[str] = None
    description: Optional[str] = None

    # Lazy loaded maps
    # TODO populate these maps
    _privilege_to_rule: dict = {}
    _role_to_promotion_rule: dict = {}


class Principle(BaseModel):
    """Subject about which rules are tested."""

    class Config:
        extra = Extra.allow

    id: Optional[str] = None
    roles: Optional[Set[str]] = None

    @root_validator(pre=True)
    @classmethod
    def _id_or_roles_present(cls, values):
        if "id" not in values and "roles" not in values:
            raise ValueError("either id or roles must have a meaningful value")
