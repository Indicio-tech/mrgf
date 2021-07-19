"""Setup MRGF plugin."""

import json
from typing import List, TextIO, cast

from aries_cloudagent.config.injection_context import InjectionContext
from pydantic import BaseModel

from .models import (
    Condition,
    Definition,
    Duty,
    GovernaceFramework,
    JsonLDDocument,
    NamedObject,
    Privilege,
    Rule,
)


class Config(BaseModel):
    """Configuration model for MRGF plugin."""

    paths: List[str] = []
    urls: List[str] = []


async def setup(context: InjectionContext):
    """Set up plugin for use in ACA-Py."""
    plugin_config = context.settings.get("plugin_config")
    plugin_config = cast(dict, plugin_config)
    if not plugin_config:
        return

    config = plugin_config.get("mrgf")
    if not config:
        return

    config = Config(**config)
    frameworks = GovernanceFrameworks()
    context.injector.bind_instance(GovernanceFrameworks, frameworks)

    for path in config.paths:
        with open(path) as gov_file:
            framework = read_governance_file(gov_file)
        frameworks.add(framework)

    for url in config.urls:
        # TODO load urls into some structure
        pass


def read_governance_file(gov_file: TextIO) -> GovernaceFramework:
    """Read mgrf data from file."""
    gov_json = json.load(gov_file)
    return GovernaceFramework(**gov_json)


class GovernanceFrameworks:
    """Container for one or many Governance Frameworks."""

    __slots__ = ("_frameworks",)

    def __init__(self):
        self._frameworks = {}

    @staticmethod
    def _key(framework: GovernaceFramework):
        return "{}:{}".format(framework.name, framework.version)

    def add(self, framework: GovernaceFramework):
        """Add a loaded GovernaceFramework to the index."""
        key = self._key(framework)
        if key in self._frameworks:
            raise ValueError("Framework already added to index")
        self._frameworks[key] = framework

    def get(self, framework_name: str) -> GovernaceFramework:
        return self._frameworks[framework_name]


__all__ = [
    "Condition",
    "Config",
    "Definition",
    "Duty",
    "GovernaceFramework",
    "GovernaceFrameworks",
    "JsonLDDocument",
    "NamedObject",
    "Privilege",
    "Rule",
]
