"""Setup MRGFW plugin."""

from typing import List, Optional, cast

from aries_cloudagent.config.injection_context import InjectionContext
from pydantic import BaseModel


class Config(BaseModel):
    paths: List[str] = []
    urls: List[str] = []


async def setup(context: InjectionContext):
    """Setup plugin."""
    plugin_config = context.settings.get("plugin_config")
    plugin_config = cast(dict, plugin_config)
    if not plugin_config:
        return

    config = cast(Optional[dict], plugin_config.get("mrgfw"))
    if not config:
        return

    config = Config(**config)

    for path in config.paths:
        # load paths into some structure
        pass

    for url in config.urls:
        # TODO load urls into some structure
        pass
