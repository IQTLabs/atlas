CREATE FUNCTION atlas.authenticated_user(hasura_session json)
    RETURNS SETOF atlas.authenticated_user_email AS
$$
SELECT q.*
FROM (VALUES (hasura_session ->> 'x-hasura-remote-user')) q
$$ LANGUAGE sql STABLE;
