--
-- radius_authentications
--
-- 💡 Un/Comment columns to quickly customize queries. Remember the last SELECT column must not end with a `,`.
--

SELECT
    * -- all columns
    -- access_service, -- Allowed Protocols
    -- audit_session_id,
    -- authentication_method,
    -- authentication_protocol,
    -- authorization_profiles, -- ⚠ Blank for failed auths!
    -- authorization_rule, -- ⚠ Blank for failed auths!
    -- calling_station_id,
    -- checksum,
    -- credential_check,
    -- device_name,
    -- device_type,
    -- endpoint_profile,
    -- failed,
    -- failure_reason,
    -- framed_ip_address,
    -- framed_ipv6_address,
    -- id,
    -- identity_group,
    -- identity_store,
    -- ise_node,
    -- location,
    -- mdm_server_name,
    -- nas_ip_address,
    -- nas_ipv6_address,
    -- nas_port_id, -- Physical port number of the NAS (Network Access Server) originating the request
    -- nas_port_type,
    -- orig_calling_station_id,
    -- passed, -- 'Fail' for username='INVALID'
    -- policy_set_name, -- Default, Wired, etc.
    -- posture_status,
    -- response_time -- ⚠ Blank for failed auths!
    -- security_group, -- ⚠ Blank for failed auths!
    -- service_type,
    -- syslog_message_code,
    -- timestamp
    -- timestamp_timezone,
    -- user_type,
    -- username,
FROM radius_authentications
-- WHERE timestamp > sysdate - INTERVAL '10' SECOND -- last N seconds
-- WHERE timestamp > sysdate - INTERVAL '1' MINUTE  -- last N minutes
-- WHERE timestamp > sysdate - INTERVAL '1' HOUR -- last N hours
-- WHERE timestamp > sysdate - INTERVAL '1' DAY -- last N days
-- WHERE TO_CHAR(timestamp, 'YYYY-MM-DD') = '2024-11-01' -- match a timestamp by day
-- WHERE TO_CHAR(timestamp, 'YYYY-MM-DD HH24:MI:SS') = '2024-11-01 00:08:27' -- match a timestamp (YYYY-MM-DD HH24:MI:SS.ffffff)
-- WHERE timestamp > TIMESTAMP '2024-11-01 00:00:00' -- after a timestamp
-- WHERE timestamp > TIMESTAMP '2024-11-01 00:00:00' AND timestamp < TIMESTAMP '2024-11-02 00:00:00' -- time window
-- WHERE timestamp BETWEEN Date '2024-11-01' and Date '2024-11-02' -- exclusive of end date
-- WHERE timestamp_timezone < '24-APR-22 08.25.35.839000000 PM +05:30' AND timestamp_timezone > '23-APR-22 08.25.35.839000000 PM +05:30'
ORDER BY timestamp ASC -- first/oldest records
-- ORDER BY timestamp DESC -- most recent records
FETCH FIRST 10 ROWS ONLY -- limit default number of rows returned for large datasets
