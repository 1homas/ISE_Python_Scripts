SELECT
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
    nas_port_type,
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
    COUNT(timestamp) AS count
FROM radius_authentications
GROUP BY nas_port_type -- FETCH FIRST 10 ROWS ONLY