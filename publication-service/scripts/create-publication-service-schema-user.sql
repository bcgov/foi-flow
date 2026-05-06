DO $$
DECLARE
    -- SET YOUR VARIABLES HERE
    app_schema   TEXT := 'publication';
    app_user     TEXT := 'publication_service_app';
    app_password TEXT := 'change_me_now_123';
    current_db   TEXT := current_database();
BEGIN
    -- 1. Create the role if it doesn't exist
    IF NOT EXISTS (
        SELECT 1
        FROM pg_roles
        WHERE rolname = app_user
    ) THEN
        EXECUTE format(
            'CREATE ROLE %I WITH LOGIN PASSWORD %L',
            app_user,
            app_password
        );
    END IF;

    -- 2. Grant database access
    EXECUTE format(
        'GRANT CONNECT, TEMPORARY ON DATABASE %I TO %I',
        current_db,
        app_user
    );

    -- 3. Create schema owned by app user
    EXECUTE format(
        'CREATE SCHEMA IF NOT EXISTS %I AUTHORIZATION %I',
        app_schema,
        app_user
    );

    -- 4. Grant schema usage
    EXECUTE format(
        'GRANT USAGE, CREATE ON SCHEMA %I TO %I',
        app_schema,
        app_user
    );

    -- 5. Set default search path
    EXECUTE format(
        'ALTER ROLE %I SET search_path = %I, public',
        app_user,
        app_schema
    );

    -- 6. Grant privileges on existing tables/sequences
    EXECUTE format(
        'GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA %I TO %I',
        app_schema,
        app_user
    );

    EXECUTE format(
        'GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA %I TO %I',
        app_schema,
        app_user
    );

    -- 7. Set default privileges for future objects
    EXECUTE format(
        'ALTER DEFAULT PRIVILEGES IN SCHEMA %I
         GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO %I',
        app_schema,
        app_user
    );

    EXECUTE format(
        'ALTER DEFAULT PRIVILEGES IN SCHEMA %I
         GRANT USAGE, SELECT, UPDATE ON SEQUENCES TO %I',
        app_schema,
        app_user
    );

    RAISE NOTICE
        'Provisioning complete for user % on schema %',
        app_user,
        app_schema;
END
$$;