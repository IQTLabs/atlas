CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE SCHEMA atlas;

-- Remove if Team decides not to import/manage internal users. Proxy is setting headers/hasura uses headers for access control
CREATE TABLE atlas.users
(
    email      varchar(255)                              NOT NULL,
    created_at timestamp WITHOUT TIME ZONE DEFAULT now() NOT NULL,
    updated_at timestamp WITHOUT TIME ZONE DEFAULT now() NOT NULL,
    deleted_at timestamp WITHOUT TIME ZONE,
    admin      boolean                     DEFAULT FALSE NOT NULL,
    CONSTRAINT users_email_check CHECK (((email)::text <> ''::text))
);

CREATE TABLE atlas.views
(
    id              uuid                        DEFAULT public.uuid_generate_v4()                            NOT NULL,
    created_at      timestamp WITHOUT TIME ZONE DEFAULT now()                                                NOT NULL,
    updated_at      timestamp WITHOUT TIME ZONE DEFAULT now()                                                NOT NULL,
    deleted_at      timestamp WITHOUT TIME ZONE,
    title           character varying(255)                                                                   NOT NULL,
    owner_email     varchar(255),
    description     text                        DEFAULT '-- update description --'    NOT NULL,
    legend_node_label   character varying(255) DEFAULT 'Parent/Child',
    legend_edge_label   character varying(255) DEFAULT 'Connections',
    is_featured    boolean                     DEFAULT FALSE NOT NULL
);


CREATE TABLE atlas.data
(
    id              uuid                        DEFAULT public.uuid_generate_v4()                            NOT NULL,
    created_at      timestamp WITHOUT TIME ZONE DEFAULT now()                                                NOT NULL,
    updated_at      timestamp WITHOUT TIME ZONE DEFAULT now()                                                NOT NULL,
    deleted_at      timestamp WITHOUT TIME ZONE,
    source          character varying(255),
    location        character varying(255),
    api_url         character varying(255),
    headers         text[],
    query_object    character varying(255),
    query           character varying(255),
    view_id         uuid                        NOT NULL,
    network_data    jsonb,
    transformed_network_data jsonb
);


CREATE TABLE atlas.nodes
(
    id              uuid                        DEFAULT public.uuid_generate_v4()                            NOT NULL,
    created_at      timestamp WITHOUT TIME ZONE DEFAULT now()                                                NOT NULL,
    updated_at      timestamp WITHOUT TIME ZONE DEFAULT now()                                                NOT NULL,
    deleted_at      timestamp WITHOUT TIME ZONE,
    parent_key      character varying(255),
    parent_label    character varying(255),
    font_size       bigint DEFAULT 14,
    sizes_roots     bigint DEFAULT 35,
    sizes_root_child bigint DEFAULT 23,
    sizes_child_descendants         bigint DEFAULT 15,
    view_id         uuid                        NOT NULL
);

CREATE TABLE atlas.edges
(
    id              uuid                        DEFAULT public.uuid_generate_v4()                            NOT NULL,
    created_at      timestamp WITHOUT TIME ZONE DEFAULT now()                                                NOT NULL,
    updated_at      timestamp WITHOUT TIME ZONE DEFAULT now()                                                NOT NULL,
    deleted_at      timestamp WITHOUT TIME ZONE,
    classes         character varying(255),
    width                       bigint DEFAULT 10,
    curve_style                 character varying(255),
    control_point_weight        bigint DEFAULT 10,
    control_point_step_size     bigint DEFAULT 10,
    view_id         uuid                        NOT NULL
);

CREATE TABLE atlas.layouts
(
    id              uuid                        DEFAULT public.uuid_generate_v4()                            NOT NULL,
    view_id         uuid                        NOT NULL,
    name            character varying(255)      DEFAULT 'cose-bilkent',
    created_at      timestamp WITHOUT TIME ZONE DEFAULT now()                                                NOT NULL,
    updated_at      timestamp WITHOUT TIME ZONE DEFAULT now()                                                NOT NULL,
    deleted_at      timestamp WITHOUT TIME ZONE,
    -- dash cystoscape layout options
    zoom                 decimal DEFAULT 0.3,
    panning_enabled        boolean                     DEFAULT TRUE,
    user_panning_enabled     boolean                     DEFAULT TRUE,
    zooming_enabled     boolean                     DEFAULT TRUE,
    user_zooming_enabled     boolean                     DEFAULT TRUE,
    -- cose-bilkent layout options
    quality     character varying(255) DEFAULT 'default',
    node_dimensions_include_labels     boolean                     DEFAULT TRUE,
    refresh     bigint DEFAULT 30,
    fit     boolean                     DEFAULT TRUE,
    padding     bigint DEFAULT 10,
    randomize     boolean                     DEFAULT TRUE,
    node_repulsion     bigint DEFAULT 2000000,
    ideal_edge_length     bigint DEFAULT 120,
    edge_elasticity     decimal DEFAULT 0.9,
    nesting_factor     decimal DEFAULT 0.9,
    gravity     decimal DEFAULT 0.25,
    num_iter     bigint DEFAULT 280000000,
    tile        boolean                     DEFAULT TRUE,
    animate     character varying(255) DEFAULT 'end',
    animation_duration     bigint DEFAULT 500,
    tiling_padding_vertical     bigint DEFAULT 10,
    tiling_padding_horizontal     bigint DEFAULT 10,
    gravity_range_compound    decimal DEFAULT 200000000,
    gravity_compound     bigint DEFAULT 2400,
    gravity_range     decimal DEFAULT 1.5,
    initial_energy_on_incremental     decimal DEFAULT 0.1
);

ALTER TABLE ONLY atlas.users
    ADD CONSTRAINT users_email_key UNIQUE (email);
ALTER TABLE ONLY atlas.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (email);
ALTER TABLE ONLY atlas.views
    ADD CONSTRAINT views_pkey PRIMARY KEY (id);
ALTER TABLE ONLY atlas.data
    ADD CONSTRAINT data_pkey PRIMARY KEY (id);
ALTER TABLE ONLY atlas.nodes
    ADD CONSTRAINT nodes_pkey PRIMARY KEY (id);
ALTER TABLE ONLY atlas.edges
    ADD CONSTRAINT edges_pkey PRIMARY KEY (id);
ALTER TABLE ONLY atlas.layouts
    ADD CONSTRAINT layouts_pkey PRIMARY KEY (id);
ALTER TABLE ONLY atlas.data
    ADD CONSTRAINT data_view_id_fkey FOREIGN KEY (view_id) REFERENCES atlas.views (id) ON DELETE CASCADE;
ALTER TABLE ONLY atlas.nodes
    ADD CONSTRAINT nodes_view_id_fkey FOREIGN KEY (view_id) REFERENCES atlas.views (id) ON DELETE CASCADE;
ALTER TABLE ONLY atlas.edges
    ADD CONSTRAINT edges_view_id_fkey FOREIGN KEY (view_id) REFERENCES atlas.views (id) ON DELETE CASCADE;
ALTER TABLE ONLY atlas.layouts
    ADD CONSTRAINT layouts_view_id_fkey FOREIGN KEY (view_id) REFERENCES atlas.views (id) ON DELETE CASCADE;

-- functions
CREATE OR REPLACE FUNCTION atlas.authenticated_user(hasura_session json)
 RETURNS SETOF atlas.users AS
  $$
      SELECT *
      FROM atlas.users
      WHERE email = hasura_session ->> 'x-hasura-remote-user'
  $$ LANGUAGE sql STABLE;

-- views
CREATE VIEW atlas.my_views AS
    SELECT * FROM atlas.views;