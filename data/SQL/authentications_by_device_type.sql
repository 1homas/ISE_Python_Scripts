-- From the ISE Data Connect Guides' RADIUS Authentication Summary Examples
-- https://developer.cisco.com/docs/dataconnect/guides/#radius-authentication-summary
SELECT device_type,
  SUM(passed_count) AS passed,
  SUM(failed_count) AS failed,
  SUM(passed_count) + SUM(failed_count) AS total,
  ROUND(
    to_char(
      (
        (
          SUM(failed_count) / (SUM(passed_count) + SUM(failed_count))
        ) * 100
      )
    ),
    2
  ) AS failed_pct,
  ROUND(
    to_char(
      SUM(total_response_time) /(SUM(passed_count) + SUM(failed_count))
    ),
    2
  ) AS total_response_time,
  MAX(max_response_time) AS max_response_time
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
FROM radius_authentication_summary
GROUP BY device_type
ORDER BY device_type ASC