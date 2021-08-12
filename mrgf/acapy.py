"""Elements for integrating with ACA-Py."""
from typing import Set, Union
from aries_cloudagent.connections.models.conn_record import ConnRecord
from aries_cloudagent.core.profile import ProfileSession
from aries_cloudagent.messaging.request_context import RequestContext

from .governance_framework import GovernanceFramework, Principal


class NoLoadedFramework(Exception):
    """Raised when no framework is loaded."""


async def connection_to_principal(
    session: ProfileSession, connection: Union[str, ConnRecord]
) -> Principal:
    """Return principal from connection."""
    if isinstance(connection, str):
        conn_record = ConnRecord.retrieve_by_id(session, connection)
    elif isinstance(connection, ConnRecord):
        conn_record = connection
    else:
        raise TypeError("connection must be connection id or ConnRecord")

    framework = session.inject(GovernanceFramework, required=False)
    if not framework:
        raise NoLoadedFramework(
            "No machine readable governance framework found in context"
        )

    metadata = await conn_record.metadata_get_all(session)

    initial = Principal(id=conn_record.connection_id, **metadata)
    privileges: Set[str] = framework.evaluate(initial)
    return Principal(id=conn_record.connection_id, privileges=privileges, **metadata)


async def request_context_principal_finder(context: RequestContext) -> Principal:
    """Retrieve connection and metadata, evaluate MRGF rules, and return Principal."""
    async with context.session() as session:
        return await connection_to_principal(session, context.connection_record)


async def request_handler_principal_finder(*args, **kwargs) -> Principal:
    """Extract context and return principal."""
    [context] = [arg for arg in args if isinstance(arg, RequestContext)]
    return await request_context_principal_finder(context)
