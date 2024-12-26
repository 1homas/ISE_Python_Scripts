--
-- Practical radius_errors_view
--
-- 💡 Un/Comment columns to quickly customize queries. Remember the last SELECT column must not end with a `,`.
--
-- Author: Thomas Howard, thomas@cisco.com
-- License: MIT - https://mit-license.org
--

SELECT
  TO_CHAR(timestamp, 'YYYY-MM-DD HH24:MI:SS') AS timestamp, -- drop fractional seconds
  -- timestamp_timezone, -- OK for thin client
  -- id AS id, -- session ID?
  -- audit_session_id, -- unique numeric string identifying the server session
  calling_station_id AS mac, -- endpoint MAC address
  username, -- user's claimed identity
  -- user_type, -- sometimes `User`; unreliable
  network_device_name AS device,
  nas_ip_address,
  SUBSTR(device_type, 18) AS device_ndg, -- 'All Device Types' network device group (NDG)
  SUBSTR(location, 15) AS location, -- 'All Locations' network device group (NDG)
  -- nas_ipv6_address, -- NULL if IPv4
  -- nas_port_id, -- ⚠ always null for Meraki?
  nas_port_type, -- NULL, Ethernet, Wireless - IEEE 802.11, etc.

  authentication_method AS authn_method, -- Example: MSCHAPV2
  authentication_protocol AS authn_protocol, -- Example: PEAP (EAP-MSCHAPv2), EAP-TLS
  -- authorization_policy, -- ⚠ always null
  message_code AS code, -- Example: 5411
  response, -- NULL or `{RadiusPacketType=Drop; }`
  -- ise_node,
  -- mdm_server_name,
  access_service AS allowed_protocols, -- allowed protocols
  -- identity_store,
  -- identity_group,
  service_type, -- NULL, Framed, Call Check, etc.
  -- selected_authorization_profiles, -- authorization profile used after authentication
  -- posture_status,
  CASE WHEN LENGTH(failure_reason) > 50 THEN SUBSTR(failure_reason, 1, 49) || '⋯' ELSE failure_reason END AS failure_reason, -- ⚠ long message text
  -- message_text, -- same as failure_reason without error code
  -- execution_steps, # very long list of step numbers
  -- other_attributes -- very long string of RADIUS attributes; useful for debugging
  -- other_attributes_string, -- long list of RADIUS attributes 
  -- passed AS pass, -- ⚠ always 'Fail'
  -- failed AS fail, -- ⚠ always 1
  -- authentication_policy, -- ⚠ always null
  -- credential_check, -- ⚠ always null
  -- endpoint_profile, -- ⚠ always null
  -- framed_ip_address, -- ⚠ always null
  -- framed_ipv6_address, -- ⚠ always null
  -- security_group AS SGT, -- ⚠ always null
  response_time AS resp_ms -- milliseconds
FROM radius_errors_view
-- WHERE timestamp > sysdate - INTERVAL '10' SECOND -- last N seconds
-- WHERE timestamp > sysdate - INTERVAL '1' MINUTE  -- last N minutes
-- WHERE timestamp > sysdate - INTERVAL '1' HOUR -- last N hours
WHERE timestamp > sysdate - INTERVAL '1' DAY -- last N days
ORDER BY timestamp ASC -- first/oldest records
-- ORDER BY timestamp DESC -- most recent records
-- FETCH FIRST 10 ROWS ONLY -- limit default number of rows returned for large datasets
