"""Setup MRGF plugin."""

import json
import logging
from typing import Optional

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
from .acapy import RequestHandlerPrincipleFinder


LOGGER = logging.getLogger(__name__)


class Config(BaseModel):
    """Configuration model for MRGF plugin."""

    path: Optional[str] = None
    url: Optional[str] = None


async def setup(context: InjectionContext, config: Optional[Config] = None):
    """Set up plugin for use in ACA-Py."""
    if not config:
        try:
            config = Config(**context.settings["plugin_config"]["mrgf"])
        except KeyError:
            LOGGER.warning("No MRGF configuration found")
            return

    framework = None
    if config.path:
        with open(config.path) as gov_file:
            gov_json = json.load(gov_file)
            framework = GovernanceFramework(**gov_json)

    if config.url and not framework:
        # TODO load from url
        pass

    if framework:
        context.injector.bind_instance(GovernanceFramework, framework)
    else:
        LOGGER.warning("No governance file loaded")


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
    "RequestHandlerPrincipleFinder",
]
