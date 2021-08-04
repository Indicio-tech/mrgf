"""Elements for integrating with ACA-Py."""
from typing import Set
from aries_cloudagent.messaging.request_context import RequestContext
from aries_cloudagent.messaging.responder import BaseResponder

from .governance_framework import GovernanceFramework, Principal


class NoLoadedFramework(Exception):
    """Raised when no framework is loaded."""


async def request_handler_principle_finder(
    handler, context: RequestContext, responder: BaseResponder
) -> Principal:
    """Retrieve connection and metadata, evaluate MRGF rules, and return Principal."""
    conn = context.connection_record
    framework = context.inject(GovernanceFramework, required=False)
    if not framework:
        raise NoLoadedFramework(
            "No machine readable governance framework found in context"
        )

    async with context.session() as session:
        metadata = await conn.metadata_get_all(session)

        initial_principal = Principal(id=conn.connection_id, **metadata)
        privileges: Set[str] = framework.evaluate(initial_principal)
        return Principal(id=conn.connection_id, privileges=privileges, **metadata)
