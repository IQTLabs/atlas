CREATE OR REPLACE FUNCTION atlas.search_data_tsvector(keyword varchar, data_id uuid) RETURNS SETOF atlas.text_result AS
$$
    DECLARE
        key record;
        sql VARCHAR;
        i integer;
        counter integer := 0;
        labels record;
    BEGIN
        keyword := TRIM(BOTH FROM keyword);
        SELECT COUNT(*) INTO i FROM (SELECT DISTINCT jsonb_object_keys(t.data -> 'attributes')
                FROM atlas.data d
                CROSS JOIN LATERAL jsonb_to_recordset(d.transformed_network_data) AS t("data" jsonb) WHERE id = data_id) as temp;
        keyword := lower(keyword);
        sql = 'SELECT t.data  ->> ''label''::text as label FROM ' ||
              'atlas.data d ' ||
              'CROSS JOIN LATERAL jsonb_to_recordset(d.transformed_network_data) AS t("data" jsonb) WHERE ' ||
              'd.id = ''' || data_id || ''' AND (to_tsvector(t.data ->> ''label'') @@ to_tsquery(REPLACE(''' || keyword || ''', '' '', '' | ''))  OR ';

        FOR key IN
            SELECT DISTINCT jsonb_object_keys(t.data -> 'attributes') AS key
                FROM atlas.data d
                CROSS JOIN LATERAL jsonb_to_recordset(d.transformed_network_data) AS t("data" jsonb)
                WHERE id = data_id
            LOOP
                counter := counter + 1;
                sql := sql || 'to_tsvector(t.data -> ''attributes'' ->> regexp_replace(''' || key || ''', ''([(")])'','''',''g'')) @@ to_tsquery(REPLACE(''' || keyword || ''', '' '', '' | ''))  ';
                IF counter < i THEN
                    sql := sql || 'OR ';
                ELSE
                    sql := sql || ')';
                END IF;
            END LOOP;
        RETURN QUERY EXECUTE sql;
    END;
$$
    LANGUAGE plpgsql STABLE
                     STRICT;