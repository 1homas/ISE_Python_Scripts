SELECT 
  mac_address,
  endpoint_ip,
  endpoint_policy,
  static_group_assignment,
  matched_value, -- Matched Certainty Factor
  custom_attributes,
  hostname,
  id,
  static_assignment,
  reg_timestamp, -- 🐞 Always 0?
  auth_store_id, -- Always blank?
  byod_reg,
  device_registrations_status,
  endpoint_id, -- Example: epid:420686389928259584
  endpoint_policy_id,
  endpoint_policy_version,
  endpoint_unique_id,
  identity_group_id,
  matched_policy_id,
  -- probe_data, -- ⚠ Error: 'utf-8' codec can't decode byte 0xbb in position 1260: invalid start byte
  mdm_guid,
  mdm_server_id,
  native_udid,
  nmap_subnet_scanid,
  phone_id,
  phone_id_type,
  portal_user,
  posture_applicable,
  posture_expiry,
  profile_server,
  unique_subject_id,
  version
FROM endpoints_data
-- FETCH FIRST 10 ROWS ONLY
