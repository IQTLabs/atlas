from flask import current_app, request
from gql import Client
from gql.transport.aiohttp import AIOHTTPTransport


def get_headers():
    if current_app.config.get("FLASK_ENV") == 'development' or current_app.config.get("FLASK_ENV") == 'public':
        return {
            'x-hasura-remote-user': 'rey@example.com',
            'x-hasura-admin-secret': current_app.config.get("HASURA_GRAPHQL_ADMIN_SECRET"),
            'x-hasura-role': 'api-user'
        }
    else:
        return {
            'x-hasura-remote-user': request.headers['x-hasura-remote-user'],
            'x-hasura-admin-secret': current_app.config.get("HASURA_GRAPHQL_ADMIN_SECRET"),
            'x-hasura-role': request.headers['x-hasura-role']
        }


async def get_hasura_connection(query):
    transport = AIOHTTPTransport(url=current_app.config.get('HASURA_GRAPHQL_API'), headers=get_headers())
    # Using `async with` on the client will start a connection on the transport
    # and provide a `session` variable to execute queries on this connection
    async with Client(
            transport=transport, fetch_schema_from_transport=True,
    ) as session:
        result = await session.execute(query)
        return result


async def get_hasura_connection_with_params(query, params):
    transport = AIOHTTPTransport(url=current_app.config.get('HASURA_GRAPHQL_API'), headers=get_headers())

    async with Client(
            transport=transport, fetch_schema_from_transport=True,
    ) as session:
        result = await session.execute(query, variable_values=params)
        return result
