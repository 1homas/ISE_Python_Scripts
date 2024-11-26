--
-- RADIUS Authentications
--
-- 💡 Un/Comment columns to quickly customize queries.
--    Remember the last SELECT column must not end with a `,`.
--
-- Author: Thomas Howard, thomas@cisco.com
-- License: MIT - https://mit-license.org
--

SELECT
    TO_CHAR(timestamp, 'YYYY-MM-DD HH24:MI:SS') AS timestamp, -- drop fractional seconds
    -- passed, -- 'Fail' for username='INVALID'
    calling_station_id,
    username,
    -- user_type,  -- ⚠ Blank?
    device_name,
    -- nas_ip_address,
    -- nas_port_id,
    -- nas_port_type,
    ise_node,
    policy_set_name, -- Default, Wired, etc.
    -- audit_session_id,
    access_service, -- Allowed Protocols
    authentication_method AS auth_method,
    authentication_protocol AS auth_protocol,
    authorization_rule AS authz_rule, -- ⚠ Blank for failed auths!
    authorization_profiles AS authz_profiles, -- ⚠ Blank for failed auths!
    -- checksum,
    -- credential_check -- Auth protocol?
    -- device_type, -- NDG
    -- failed,
    -- failure_reason,
    -- framed_ip_address,
    -- framed_ipv6_address,
    -- id,
    -- identity_group,
    -- identity_store,
    -- location, -- NDG
    -- mdm_server_name,
    -- nas_ipv6_address,
    -- orig_calling_station_id,
    -- posture_status, 
    -- response_time -- ⚠ Blank for failed auths!
    -- security_group, -- ⚠ Blank for failed auths!
    -- service_type,
    -- syslog_message_code,
    response_time
FROM radius_authentications
-- WHERE username = 'INVALID'
-- WHERE timestamp > sysdate - INTERVAL '10' SECOND -- last N seconds
-- WHERE timestamp > sysdate - INTERVAL '1' MINUTE  -- last N minutes
WHERE timestamp > sysdate - INTERVAL '1' HOUR -- last N hours
-- WHERE timestamp > sysdate - INTERVAL '1' DAY -- last N days
-- WHERE TO_CHAR(timestamp, 'YYYY-MM-DD') = '2024-11-01' -- match a timestamp by day
-- WHERE TO_CHAR(timestamp, 'YYYY-MM-DD HH24:MI:SS') = '2024-11-01 00:08:27' -- match a timestamp (YYYY-MM-DD HH24:MI:SS.ffffff)
-- WHERE timestamp > TIMESTAMP '2024-11-01 00:00:00' -- after a timestamp
-- WHERE timestamp > TIMESTAMP '2024-11-01 00:00:00' AND timestamp < TIMESTAMP '2024-11-02 00:00:00' -- time window
-- WHERE timestamp BETWEEN Date '2024-11-01' and Date '2024-11-02' -- exclusive of end date
ORDER BY timestamp ASC -- first/oldest records
-- ORDER BY timestamp DESC -- most recent records
-- FETCH FIRST 50 ROWS ONLY -- limit default number of rows returned for large datasets
