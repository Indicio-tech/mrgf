"""Setup MRGF plugin."""

import json
import logging
from typing import Optional, TextIO

from aries_cloudagent.config.injection_context import InjectionContext
from pydantic import BaseModel

from .governance_framework import (
    Condition,
    Definition,
    Duty,
    GovernanceFramework,
    JsonLDDocument,
    NamedObject,
    Privilege,
    Principal,
    Rule,
)
from .selector import Selector


LOGGER = logging.getLogger(__name__)


class Config(BaseModel):
    """Configuration model for MRGF plugin."""

    path: Optional[str] = None
    url: Optional[str] = None


async def setup(context: InjectionContext):
    """Set up plugin for use in ACA-Py."""
    try:
        config = Config(**context.settings["plugin_config"]["mrgf"])
    except KeyError:
        LOGGER.warning("No MRGF configuration found")
        return

    framework = None
    if config.path:
        with open(config.path) as gov_file:
            framework = read_governance_file(gov_file)

    if config.url and not framework:
        # TODO load from url
        pass

    if framework:
        context.injector.bind_instance(GovernanceFramework, framework)
    else:
        LOGGER.warning("No governance file loaded")


def read_governance_file(gov_file: TextIO) -> GovernanceFramework:
    """Read mgrf data from file."""
    gov_json = json.load(gov_file)
    return GovernanceFramework(**gov_json)


__all__ = [
    "Condition",
    "Config",
    "Definition",
    "Duty",
    "GovernanceFramework",
    "JsonLDDocument",
    "NamedObject",
    "Privilege",
    "Principal",
    "Rule",
    "Selector",
]
