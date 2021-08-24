"""MRGF Admin Routes."""

import logging
from aiohttp import web
from aiohttp_apispec import docs
from aries_cloudagent.admin.request_context import AdminRequestContext
from .governance_framework import GovernanceFramework


LOGGER = logging.getLogger(__name__)


@docs(tags=["mrgf"], summary="Set MRGF loaded by agent.")
async def set_mrgf(request: web.Request):
    """Set MRGF."""
    context: AdminRequestContext = request["context"]
    body = await request.json() if request.body_exists else None
    if not body:
        raise web.HTTPBadRequest(reason="Expected mrgf as json body")

    try:
        mrgf = GovernanceFramework(**body)
    except ValueError as err:
        raise web.HTTPBadRequest(reason="Bad MRGF passed: {}".format(err))

    LOGGER.warning("Replacing MRGF with new MRGF from routes: %s", mrgf)
    context.injector.bind_instance(GovernanceFramework, mrgf)
    return web.json_response({"success": True})
