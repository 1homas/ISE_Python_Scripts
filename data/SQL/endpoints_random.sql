--
-- endpoints_random
-- Collection of all data related to endpoints in ISE.
--
-- ⚡ Attributes updated in real time
-- ⧗ The other attributes will be synchronized with a delay of up to 12 hours.
--

SELECT
  TO_CHAR(create_time, 'YYYY-MM-DD HH24:MI:SS') AS created, -- time when record added; drop fractional seconds
  mac_address, -- endpoint MAC address
  CASE WHEN REGEXP_LIKE(mac_address, '^.[26AE].*', 'i') THEN SUBSTR(mac_address, 2, 1) ELSE '✕' END AS random, -- random MAC feature column ✔|✕
  -- create_time, -- ⚠ not supported in thin mode
  -- update_time, -- ⚠ not supported in thin mode
  endpoint_ip, -- the IP address of the endpoint
  endpoint_policy, -- ⚡ endpoint profile classification
  matched_value, -- ⚡ Matched Certainty Factor (CF)
  -- custom_attributes, -- the custom attributes; 🐞 UUIDs instead of attribute names and no separators
  -- hostname, -- ⚡ DNS hostname of the endpoint, if any
  static_assignment AS is_static, -- ⚡ the endpoint static assignment status
  static_group_assignment AS static_group, -- ⚡ endpoint statically assigned to user ID group
  -- anomalous_behaviour, -- ⚡
  -- aup_accepted, -- ⚡
  -- auth_store_id, -- ⧗ the auth store ID; Always blank? -- 
  -- byod_reg, -- ⧗ the BYOD Registration status 🐞 byod_reg or byod_registered?
  -- byod_registered, -- ⚡ the BYOD Registration status
  -- device_identifier, -- ⚡
  -- device_reg_status, -- ⚡ 🐞 device_reg_status or device_registrations_status?
  -- device_registrations_status,  -- ⧗ if device is registered
  -- endpoint_id, -- ⧗ the EPID of the endpoint, Example: epid:420686389928259584
  -- endpoint_policy_id, -- ⧗ the unique ID of the endpoint policy used
  -- endpoint_policy_version, -- ⧗ The version of endpoint policy used
  -- endpoint_unique_id,-- ⧗-- Endpoint unique ID. What is special about this?
  -- epid, -- ⚡
  -- host_name, -- ⚡ 🐞 hostname or host_name?
  -- hostname, -- the hostname of the endpoint
  -- id, -- Database unique ID
  -- identity_group_id, -- ⚡ unique ID of UserIdentityGroup of the endpoint
  -- last_aup_accepted_timestamp, -- ⚡
  -- matched_policy_id, -- ⚡ the ID of profiling used
  -- mdm_compliant_failure_reason, -- ⚡
  -- mdm_compliant, -- ⚡
  -- mdm_diskencrypted, -- ⚡
  -- mdm_enrolled, -- ⚡
  -- mdm_guid, -- ⚡ Endpoint MDM GUID
  -- mdm_jailbroken, -- ⚡
  -- mdm_lastcheckin_timestamp, -- ⚡
  -- mdm_manufacturer, -- ⚡
  -- mdm_model, -- ⚡
  -- mdm_os_version, -- ⚡
  -- mdm_phone_num, -- ⚡
  -- mdm_pinlockset, -- ⚡
  -- mdm_provider, -- ⚡
  -- mdm_serial_num, -- ⚡
  -- mdm_server_id, -- ⚡ Endpoint MDM server ID
  -- mdm_server_name, -- ⚡
  -- mdm_serverreachable, -- ⚡
  -- mdm_updatetimestamp, -- ⚡
  -- mdm_user_notified, -- ⚡
  -- mdmimei, -- ⚡ 🐞 mdmimei or mdm_imei ?
  -- native_udid, -- ⧗ Endpoint native UDID
  -- nmap_subnet_scan_id, -- ⚡ NMAP subnet can ID of end points 🐞 nmap_subnet_scan_id or nmap_subnet_scanid ?
  -- nmap_subnet_scanid, -- ⧗ NMAP subnet can ID of end points
  -- phone_id_type, -- ⚡ Endpoint phone ID type
  -- phone_id, -- ⚡ Endpoint phone ID
  -- portal_user, -- ⚡ the portal user
  -- posture_applicable, -- ⚡ if Posture is Applicable
  -- posture_expiry, -- ⧗ the posture expiry
  -- probe_data, -- ⧗ All the probe data acquired during profiling. ⚠ Error: 'utf-8' codec can't decode byte 0xbb in position 1260: invalid start byte
  -- profile_server, -- ⧗ the ISE node that profiled the endpoint
  -- reg_timestamp, -- ⧗ the registered timestamp; 0 if not registered? 
  -- unique_subject_id, -- ⚡ Endpoint subject ID
  -- update_time, -- ⧗ Time when record last updated. Used to calculate `InactiveDays` 🛑 (TIMESTAMP(6)+TZ)
  version -- ⧗ the version
FROM endpoints_data
-- WHERE REGEXP_LIKE(mac_address, '^.[26AE].*', 'i') -- random MACs only
ORDER BY mac_address ASC
-- FETCH FIRST 10 ROWS ONLY -- limit default number of rows returned for large datasets
