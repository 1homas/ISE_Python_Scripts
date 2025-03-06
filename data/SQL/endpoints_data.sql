--
-- endpoints_data
--

SELECT
  mac_address,
  CAST(create_time AS TIMESTAMP) AS create_time, -- ⚠ cast to DATE because TIMESTAMP_TIMEZONE not supported in OracleDB's thin mode
  CAST(update_time AS TIMESTAMP) AS update_time, -- ⚠ cast to DATE because TIMESTAMP_TIMEZONE not supported in OracleDB's thin mode
  mac_address, -- endpoint MAC address
  endpoint_ip, -- the IP address of the endpoint
  endpoint_policy, -- ⚡ endpoint profile classification
  matched_value AS cf, -- ⚡ Matched Certainty Factor (CF)
  static_assignment AS is_static, -- ⚡ the endpoint static assignment status
  static_group_assignment AS static_group, -- ⚡ endpoint statically assigned to user ID group
  custom_attributes, -- ⧗ the custom attributes; 🐞 UUIDs instead of attribute names and no separators
  hostname, -- ⚡ DNS hostname of the endpoint, if any
  auth_store_id, -- ⧗ the auth store ID; Always blank? -- 
  byod_reg, -- ⧗ the BYOD Registration status 🐞 byod_reg or byod_registered?
  device_registrations_status,  -- ⧗ if device is registered
  endpoint_id, -- ⧗ the EPID of the endpoint, Example: epid:420686389928259584
  endpoint_policy_id, -- ⧗ the unique ID of the endpoint policy used
  endpoint_policy_version, -- ⧗ The version of endpoint policy used
  endpoint_unique_id,-- ⧗-- Endpoint unique ID. What is special about this?
  hostname, -- the hostname of the endpoint
  id, -- Database unique ID
  identity_group_id, -- ⚡ unique ID of UserIdentityGroup of the endpoint
  matched_policy_id, -- ⚡ the ID of profiling used
  native_udid, -- ⧗ Endpoint native UDID
  nmap_subnet_scanid, -- ⧗ NMAP subnet can ID of end points
  phone_id_type, -- ⚡ Endpoint phone ID type
  phone_id, -- ⚡ Endpoint phone ID
  portal_user, -- ⚡ the portal user
  posture_applicable, -- ⚡ if Posture is Applicable
  posture_expiry, -- ⧗ the posture expiry
  -- probe_data, -- ⧗ All the probe data acquired during profiling. ⚠ Error: 'utf-8' codec can't decode byte 0xbb in position 1260: invalid start byte
  profile_server, -- ⧗ the ISE node that profiled the endpoint
  reg_timestamp, -- ⧗ the registered timestamp; 0 if not registered? 
  unique_subject_id, -- ⚡ Endpoint subject ID
  version
FROM endpoints_data
-- ORDER BY create_time ASC
-- ORDER BY mac_address ASC
-- ORDER BY update_time DESC
FETCH FIRST 10 ROWS ONLY -- limit default number of rows returned for large datasets
