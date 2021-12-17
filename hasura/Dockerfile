FROM hasura/graphql-engine:v1.3.3.cli-migrations-v2

ENV  HASURA_GRAPHQL_ENABLE_CONSOLE="false"
ENV  HASURA_GRAPHQL_ENABLED_LOG_TYPES="startup, http-log, query-log"
ENV  HASURA_GRAPHQL_SERVER_PORT=8082
ENV  HASURA_GRAPHQL_ENABLE_TELEMETRY="false"
ENV  HASURA_GRAPHQL_MIGRATIONS_DIR="/migrations"
ENV  HASURA_GRAPHQL_METADATA_DIR="/metadata"

EXPOSE 8082

COPY migrations /migrations
COPY metadata /metadata
