SELECT -- ⓘ Request
  timestamp,
  failed,
  calling_station_id,
  username,
  failure_reason,
  device_name,
  nas_port_id,
  nas_port_type,
  response_time,
  -- audit_session_id,
  -- passed, -- 'Fail' for username='INVALID'
  -- '1' for username='INVALID'
  -- syslog_message_code,
  -- checksum,
  -- ⓘ Endpoint
  -- framed_ip_address,
  -- orig_calling_station_id,
  -- framed_ipv6_address,
  -- ⓘ User
  user_type,
  -- blank?
  -- id,
  -- service_type,
  -- access_service, -- Allowed Protocols
  -- ⓘ NAD
  -- device_type, -- NDG
  -- location, -- NDG
  -- nas_ip_address,
  -- nas_ipv6_address,
  -- ⓘ Auth
  -- identity_store,
  -- identity_group,
  -- authentication_method,
  -- authentication_protocol,
  -- credential_check -- Auth protocol?
  -- ⓘ Policy
  ise_node,
  policy_set_name -- Default, Wired, etc.
  -- authorization_rule, -- 💡 Blank for failed auths!
  -- authorization_profiles, -- 💡 Blank for failed auths!
  -- security_group, -- 💡 Blank for failed auths!
  -- response_time
  -- 💡 Blank for failed auths!
  -- posture_status,
  -- mdm_server_name,
FROM radius_authentications
WHERE username = 'INVALID'
ORDER BY username ASC
-- FETCH FIRST 10 ROWS ONLY