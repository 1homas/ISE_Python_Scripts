--
-- Show the first time an endpoint was seen (`create_time`) by ISE via RADIUS authentication.
-- Includes random MAC detection (2nd digit is 26AE).
-- Optionally filter for by time interval.
--
-- 💡 Un/Comment columns to quickly customize queries. Remember the last SELECT column must not end with a `,`.
--
-- Author: Thomas Howard, thomas@cisco.com
-- License: MIT - https://mit-license.org
--

SELECT
    mac_address,
    -- CASE WHEN REGEXP_LIKE(mac_address, '^.[26AE].*', 'i') THEN SUBSTR(mac_address, 2, 1) ELSE ' ' END AS rand, -- random MAC feature column
    CASE WHEN REGEXP_LIKE(mac_address, '^.[26AE].*', 'i') THEN '✔' ELSE ' ' END AS rand, -- random MAC feature column: ✔ ⚀, ⚁, ⚂, ⚃, ⚄, ⚅
    TO_CHAR(create_time, 'YYYY-MM-DD HH24:MI:SS') AS created, -- time when record added; drop fractional seconds
    -- update_time, -- time when record last updated ⚠timestamp+timezone!
    endpoint_ip,
    endpoint_policy, -- endpoint profile classification
    -- static_group_assignment AS static_grp,
    -- static_assignment AS static, -- 
    matched_value AS cf, -- Matched Certainty Factor (CF)
    -- custom_attributes, -- 🐞 ugly UUIDs instead of attribute names and no separators
    -- hostname,
    -- id,
    -- reg_timestamp, -- 0 if not registered?
    -- auth_store_id, -- Always blank?
    -- byod_reg, -- BYOD registration status
    -- device_registrations_status, -- device is registered
    -- endpoint_id, -- Example: epid:420686389928259584
    -- endpoint_policy_id,
    -- endpoint_policy_version,
    -- endpoint_unique_id,
    -- identity_group_id,
    -- matched_policy_id,
    -- probe_data, -- ⚠ Error: 'utf-8' codec can't decode byte 0xbb in position 1260: invalid start byte -- probe data acquired during profiling
    -- mdm_guid,
    -- mdm_server_id,
    -- native_udid,
    -- nmap_subnet_scanid,
    -- phone_id,
    -- phone_id_type,
    -- portal_user,
    -- posture_applicable,
    -- posture_expiry,
    -- profile_server,
    -- unique_subject_id,
    version AS ver
FROM endpoints_data
-- WHERE create_time > sysdate - INTERVAL '10' SECOND -- last N seconds
-- WHERE create_time > sysdate - INTERVAL '1' MINUTE  -- last N minutes
-- WHERE create_time > sysdate - INTERVAL '1' HOUR -- last N hours
WHERE create_time > sysdate - INTERVAL '1' DAY -- last N days
ORDER BY created DESC -- first/oldest records
-- ORDER BY created DESC -- most recent records
-- FETCH FIRST 10 ROWS ONLY -- limit default number of rows returned for large datasets
