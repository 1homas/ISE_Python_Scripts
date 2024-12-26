--
-- ISE Endpoints with an 'Unknown' endpoint profile.
--
-- 💡 Un/Comment columns to quickly customize queries. Remember the last SELECT column must not end with a `,`.
--
-- Author: Thomas Howard, thomas@cisco.com
-- License: MIT - https://mit-license.org
--

SELECT
  TO_CHAR(create_time, 'YYYY-MM-DD HH24:MI:SS') AS created, -- Time when record added; drop milliseconds. ⚠ (TIMESTAMP(6)+TZ)
  mac_address, -- MAC address of the endpoint
  -- CASE WHEN REGEXP_LIKE(mac_address, '^.[26AE].*', 'i') THEN '✔' END AS random, -- Indicator: ✔
  -- endpoint_ip, -- the IP address of the endpoint
  endpoint_policy, -- matched endpoint profiling policy
  matched_value AS cf, -- Matched Certainty Factor (CF)
  -- auth_store_id, -- the auth store ID
  -- byod_reg, -- the BYOD Registration status
  -- custom_attributes, -- the custom attributes
  -- device_registrations_status, -- if device is registered
  -- endpoint_id, -- the EPID of the endpoint
  -- endpoint_policy_id, -- the unique ID of the endpoint policy used
  -- endpoint_policy_version, -- The version of endpoint policy used
  -- endpoint_unique_id, -- Endpoint unique ID. What is special about this?
  -- hostname, -- the hostname of the endpoint
  -- id, -- Database unique ID
  -- identity_group_id, -- unique ID of UserIdentityGroup of the endpoint
  -- matched_policy_id, -- the ID of profiling used
  -- mdm_guid, -- Endpoint MDM GUID
  -- mdm_server_id, -- Endpoint MDM server ID
  -- native_udid, -- Endpoint native UDID
  -- nmap_subnet_scanid, -- NMAP subnet can ID of end points
  -- phone_id_type, -- Endpoint phone ID type
  -- phone_id, -- Endpoint phone ID
  -- portal_user, -- the portal user
  -- posture_applicable, -- if Posture is Applicable
  -- posture_expiry, -- the posture expiry
  -- probe_data, -- all the probe data acquired during profiling. Error: 'utf-8' codec can't decode byte
  -- profile_server, -- the ISE node that profiled the endpoint
  -- reg_timestamp, -- the registered timestamp
  -- static_assignment AS is_static, -- the endpoint static assignment status
  -- static_group_assignment AS static_group,  -- endpoint statically assigned to user ID group
  -- unique_subject_id, -- Endpoint subject ID
  -- update_time, -- Time when record last updated. Used to calculate `InactiveDays` 🛑 (TIMESTAMP(6)+TZ)
  version AS ver -- the version
FROM endpoints_data
WHERE endpoint_policy = 'Unknown'
ORDER BY create_time ASC
-- ORDER BY mac_address ASC
