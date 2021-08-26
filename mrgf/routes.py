"""MRGF Admin Routes."""

import logging
from aiohttp import web
from aiohttp_apispec import docs
from aries_cloudagent.admin.request_context import AdminRequestContext
from .governance_framework import GovernanceFramework


LOGGER = logging.getLogger(__name__)
MRGF_RFC = (
    "https://github.com/hyperledger/aries-rfcs/blob/main/concepts/"
    "0430-machine-readable-governance-frameworks"
)


@docs(
    tags=["mrgf"],
    summary="Set MRGF loaded by agent.",
    parameters=[
        {
            "in": "body",
            "required": True,
            "name": "body",
            "schema": {"type": "object"},
            "description": "Raw MRGF json",
        }
    ],
)
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


async def register(app: web.Application):
    """Register routes."""

    app.add_routes(
        [
            web.post("/mrgf", set_mrgf),
        ]
    )


def post_process_routes(app: web.Application):
    """Amend swagger API."""

    # Add top-level tags description
    if "tags" not in app._state["swagger_dict"]:
        app._state["swagger_dict"]["tags"] = []
    app._state["swagger_dict"]["tags"].append(
        {
            "name": "mrgf",
            "description": "Manage Machine Readable Governance Frameworks",
            "externalDocs": {"description": "Specification", "url": MRGF_RFC},
        }
    )
