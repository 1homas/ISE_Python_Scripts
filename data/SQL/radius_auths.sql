--
-- RADIUS Authentications
--
-- 💡 Un/Comment columns to quickly customize queries. Remember the last SELECT column must not end with a `,`.
--
-- Author: Thomas Howard, thomas@cisco.com
-- License: MIT - https://mit-license.org
--

SELECT
    TO_CHAR(timestamp, 'YYYY-MM-DD HH24:MI:SS') AS timestamp, -- drop fractional seconds
    -- passed, -- 'Fail' for username='INVALID'
    failed,
    failure_reason,
    response_time,
    calling_station_id,
    username,
    user_type,  -- ⚠ Blank?
    device_name,
    nas_ip_address,
    nas_port_id,
    nas_port_type,
    ise_node,
    policy_set_name -- Default, Wired, etc.
    -- access_service, -- Allowed Protocols
    -- audit_session_id,
    -- authentication_method,
    -- authentication_protocol,
    -- authorization_profiles, -- ⚠ Blank for failed auths!
    -- authorization_rule, -- ⚠ Blank for failed auths!
    -- checksum,
    -- credential_check -- Auth protocol?
    -- device_type, -- NDG
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
FROM radius_authentications
-- WHERE username = 'INVALID'
-- WHERE timestamp_timezone > '23-APR-22 08.25.35.839000000 PM +05:30' AND timestamp_timezone < '24-APR-22 08.25.35.839000000 PM +05:30'
ORDER BY timestamp ASC -- first/oldest records
-- ORDER BY timestamp DESC -- most recent records
FETCH FIRST 10 ROWS ONLY -- limit default number of rows returned for large datasets
