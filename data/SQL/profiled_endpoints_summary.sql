--
-- profiled_endpoints_summary
--
-- 💡 Un/Comment columns to quickly customize queries. Remember the last SELECT column must not end with a `,`.
--

SELECT
    * -- all columns
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
-- ORDER BY timestamp ASC -- first/oldest records
ORDER BY timestamp DESC -- most recent records
FETCH FIRST 10 ROWS ONLY -- limit default number of rows returned for large datasets
