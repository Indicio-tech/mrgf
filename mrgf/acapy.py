"""Elements for integrating with ACA-Py."""
from typing import Callable, Sequence, Set, Union, cast
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
        conn_record = await ConnRecord.retrieve_by_id(session, connection)
    elif isinstance(connection, ConnRecord):
        conn_record = connection
    else:
        raise TypeError("connection must be connection id or ConnRecord")

    conn_record = cast(ConnRecord, conn_record)
    framework = session.inject(GovernanceFramework)
    if not framework:
        raise NoLoadedFramework(
            "No machine readable governance framework found in context"
        )

    metadata = await conn_record.metadata_get_all(session)

    initial = Principal(id=conn_record.connection_id, **metadata)
    privileges: Set[str] = framework.evaluate(initial)
    return Principal(id=conn_record.connection_id, privileges=privileges, **metadata)


async def context_to_principal(context: RequestContext) -> Principal:
    """Retrieve connection and metadata, evaluate MRGF rules, and return Principal."""
    async with context.session() as session:
        return await connection_to_principal(session, context.connection_record)


async def handler_args_to_principal(*args, **kwargs) -> Principal:
    """Extract context and return principal."""
    [context] = [arg for arg in args if isinstance(arg, RequestContext)]
    return await context_to_principal(context)


async def connections_where(session: ProfileSession, condition: Callable):
    """Return connections where the principal found on connection meets condition."""
    # TODO replace this with a separate lookup table or connection metadata
    connections = cast(Sequence[ConnRecord], await ConnRecord.query(session))
    return [
        connection
        for connection in connections
        if condition(await connection_to_principal(session, connection))
    ]
