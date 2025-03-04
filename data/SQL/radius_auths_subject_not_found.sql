--
-- RADIUS Authentications - Subject Not Found
--
-- Author: Thomas Howard, thomas@cisco.com
-- License: MIT - https://mit-license.org
--

SELECT
    TO_CHAR(timestamp, 'YYYY-MM-DD HH24:MI:SS') AS timestamp, -- drop fractional seconds
    calling_station_id,
    username, -- subject
    device_name,
    policy_set_name, -- Default, Wired, etc.
    access_service, -- Allowed Protocols
    authentication_method AS auth_method,
    CASE WHEN LENGTH(failure_reason) > 40 THEN SUBSTR(failure_reason, 1, 39) || '⋯' ELSE failure_reason END AS failure_reason
    -- user_type,  -- ⚠ Blank?
    -- nas_ip_address,
    -- nas_port_id,
    -- nas_port_type,
    -- ise_node,
    -- audit_session_id,
    -- authentication_protocol AS auth_protocol,
    -- authorization_rule AS authz_rule, -- ⚠ Blank for failed auths!
    -- authorization_profiles AS authz_profiles, -- ⚠ Blank for failed auths!
    -- checksum,
    -- credential_check -- Auth protocol?
    -- device_type, -- NDG
    -- passed, -- 'Fail' for username='INVALID'
    -- failed,
    -- SUBSTR(failure_reason, 1, 50) || '⋯' AS failure_reason,
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
    -- response_time
FROM radius_authentications
WHERE failure_reason LIKE '22056%'
-- WHERE failure_reason IS NULL
-- WHERE failure_reason IS NOT NULL
-- AND failed = 1
-- AND username = 'INVALID'
-- AND timestamp > sysdate - INTERVAL '10' SECOND -- last N seconds
-- AND timestamp > sysdate - INTERVAL '1' MINUTE  -- last N minutes
-- AND timestamp > sysdate - INTERVAL '1' HOUR -- last N hours
  AND timestamp > sysdate - INTERVAL '30' DAY -- last N days
-- AND TO_CHAR(timestamp, 'YYYY-MM-DD') = '2024-11-01' -- match a timestamp by day
-- AND TO_CHAR(timestamp, 'YYYY-MM-DD HH24:MI:SS') = '2024-11-01 00:08:27' -- match a timestamp (YYYY-MM-DD HH24:MI:SS.ffffff)
-- AND timestamp > TIMESTAMP '2024-11-01 00:00:00' -- after a timestamp
-- AND timestamp > TIMESTAMP '2024-11-01 00:00:00' AND timestamp < TIMESTAMP '2024-11-02 00:00:00' -- time window
-- AND timestamp BETWEEN Date '2024-11-01' and Date '2024-11-02' -- exclusive of end date
-- GROUP BY failure_reason
ORDER BY timestamp ASC -- first/oldest records
