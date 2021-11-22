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
    body = await request.json() if request.body_exists else None
    if not body:
        raise web.HTTPBadRequest(reason="Expected mrgf as json body")

    context: AdminRequestContext = request["context"]
    framework = context.inject_or(GovernanceFramework)
    if not framework:
        raise web.HTTPBadRequest(reason="MRGF can only be modified if already present")

    try:
        loaded = GovernanceFramework(**body)
    except ValueError as err:
        raise web.HTTPBadRequest(reason="Bad MRGF passed: {}".format(err))

    LOGGER.warning("Replacing MRGF with new MRGF from routes: %s", loaded)
    framework.update(loaded)
    return web.json_response({"success": True, "mrgf": framework.dict(by_alias=True)})


@docs(
    tags=["mrgf"],
    summary="Get MRGF currently loaded by agent.",
    responses={
        "200": {
            "description": "mrgf",
            "content": {"application/json": {"schema": {"type": "object"}}},
        }
    },
)
async def get_mrgf(request: web.Request):
    """Get MRGF."""

    context: AdminRequestContext = request["context"]
    framework = context.inject_or(GovernanceFramework)
    if not framework:
        raise web.HTTPNotFound(reason="No Governance Framework loaded")
    return web.json_response(framework.dict(by_alias=True))


async def register(app: web.Application):
    """Register routes."""

    app.add_routes([web.post("/mrgf", set_mrgf), web.get("/mrgf", get_mrgf)])


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
