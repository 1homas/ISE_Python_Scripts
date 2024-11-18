--
-- RADIUS Authentications by Endpoint
--
-- Author: Thomas Howard, thomas@cisco.com
-- License: MIT - https://mit-license.org
--

SELECT
    DISTINCT calling_station_id,
    MAX(username) as username,
    COUNT(CASE WHEN passed = 'Pass' THEN 1 END) AS passed,
    COUNT(CASE WHEN passed = 'Fail' THEN 1 END) AS failed,
    COUNT(timestamp) AS total,
    ROUND( (COUNT(CASE WHEN passed = 'Fail' THEN 1 END) / (COUNT(CASE WHEN passed = 'Pass' THEN 1 END) + COUNT(CASE WHEN passed = 'Fail' THEN 1 END)) * 100), 0) AS failed_pct,
    COUNT(DISTINCT device_name) AS devices,
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
    -- device_type,
    -- location,
    -- nas_ip_address,
    -- nas_port_id, -- Physical port number of the NAS (Network Access Server) originating the request
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
    -- timestamp
    COUNT(timestamp) as count
FROM radius_authentications
GROUP BY calling_station_id
ORDER BY count DESC
-- ORDER BY calling_station_id ASC
-- ORDER BY username ASC
FETCH FIRST 50 ROWS ONLY -- limit default number of rows returned for large datasets
