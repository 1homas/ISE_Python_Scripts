--
-- radius_authentications_week
--
-- ⚠ This table is limited to only 1 week of data!
--

SELECT
    * -- all columns
    -- id,
    -- timestamp_timezone,
    -- ise_node,
    -- syslog_message_code,
    -- username,
    -- user_type,
    -- calling_station_id,
    -- access_service,
    -- framed_ip_address,
    -- identity_store,
    -- identity_group,
    -- audit_session_id,
    -- authentication_method,
    -- authentication_protocol,
    -- service_type,
    -- device_name,
    -- device_type,
    -- location,
    -- nas_ip_address,
    -- nas_port_id,
    -- nas_port_type,
    -- authorization_profiles,
    -- posture_status,
    -- security_group,
    -- failure_reason,
    -- response_time,
    -- passed,
    -- failed,
    -- credential_check,
    -- endpoint_profile,
    -- mdm_server_name,
    -- policy_set_name,
    -- authorization_rule,
    -- nas_ipv6_address,
    -- framed_ipv6_address,
    -- orig_calling_station_id,
    -- checksum,
    -- timestamp,
    -- authentication_policy,
    -- authorization_policy,
    -- nad_profile_name
FROM radius_authentications_week
ORDER BY timestamp ASC -- first/oldest records
-- ORDER BY timestamp DESC -- most recent records
FETCH FIRST 10 ROWS ONLY -- limit default number of rows returned for large datasets