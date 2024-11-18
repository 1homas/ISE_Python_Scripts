--
-- Show RADIUS Authentications stats for each Device
--
-- Author: Thomas Howard, thomas@cisco.com
-- License: MIT - https://mit-license.org
--


SELECT device_name,
  SUM(passed_count) AS passed,
  SUM(failed_count) AS failed,
  SUM(passed_count) + SUM(failed_count) AS total,
  ROUND( (SUM(failed_count) / (SUM(passed_count) + SUM(failed_count)) * 100), 2) AS failed_pct,
  ROUND(SUM(total_response_time) / (SUM(passed_count) + SUM(failed_count)), 2) AS total_response_time,
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
-- WHERE timestamp > '25-APR-22 01.49.00.000000000 PM' -- Format: 'DD-MMM-YY HH.MM.SS.mmmmmmmmm AM|PM'
-- WHERE timestamp > '20-OCT-24 01.00.00.000000000 PM' -- Format: 'DD-MMM-YY HH.MM.SS.mmmmmmmmm AM|PM'
-- WHERE TRUNC(timestamp) = '20-OCT-24' -- Format: 'DD-MMM-YY HH.MM.SS.mmmmmmmmm AM|PM'
GROUP BY device_name
ORDER BY device_name
FETCH FIRST 50 ROWS ONLY -- limit default number of rows returned for large datasets
