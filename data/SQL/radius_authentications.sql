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
-- WHERE timestamp_timezone < '24-APR-22 08.25.35.839000000 PM +05:30' AND timestamp_timezone > '23-APR-22 08.25.35.839000000 PM +05:30'
-- ORDER BY timestamp ASC -- first/oldest records
ORDER BY timestamp DESC -- most recent records
FETCH FIRST 10 ROWS ONLY -- limit default number of rows returned for large datasets

