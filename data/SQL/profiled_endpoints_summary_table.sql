SELECT *
    -- id, -- database unique ID
    -- timestamp, -- TIMESTAMP(6) Time when record added
    -- endpoint_id, -- Endpoint ID
    -- endpoint_profiLE, -- Endpoint profile
    -- source, -- Source name
    -- host, -- Host name
    -- endpoint_action_name, -- Endpoint action name
    -- message_code, -- Message code
    -- identity_group, -- Identity group name
FROM profiled_endpoints_summary
-- FETCH FIRST 10 ROWS ONLY
