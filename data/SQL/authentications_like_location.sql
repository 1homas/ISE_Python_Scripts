--
-- RADIUS Authentications for Location like example.
--
-- Author: Thomas Howard, thomas@cisco.com
-- License: MIT - https://mit-license.org
--

SELECT
    * -- all columns
    -- access_service,
    -- audit_session_id,
    -- authentication_method,
    -- authentication_protocol,
    -- authorization_profiles,
    -- authorization_rule,
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
    -- nas_port_id,
    -- nas_port_type,
    -- orig_calling_station_id,
    -- passed,
    -- policy_set_name,
    -- posture_status,
    -- response_time,
    -- security_group,
    -- service_type,
    -- syslog_message_code,
    -- timestamp
    -- timestamp_timezone,
    -- user_type,
    -- username,
FROM radius_authentications
WHERE location LIKE '%All%'
-- ORDER BY timestamp ASC -- first/oldest records
ORDER BY timestamp DESC -- most recent records
FETCH FIRST 10 ROWS ONLY -- limit default number of rows returned for large datasets
