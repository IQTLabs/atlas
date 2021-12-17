CREATE OR REPLACE FUNCTION atlas.authenticated_user(hasura_session json)
 RETURNS SETOF atlas.users AS
  $$
      SELECT *
      FROM atlas.users
      WHERE email = hasura_session ->> 'x-hasura-remote-user'
  $$ LANGUAGE sql STABLE;