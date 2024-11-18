--
-- Logical Profiles and Endpoints
--
-- 💡 Un/Comment columns to quickly customize queries. Remember the last SELECT column must not end with a `,`.
--

SELECT
    b.logical_profile,
    b.assigned_policies,
    a.mac_address
FROM
    endpoints_data a,
    logical_profiles b
WHERE a.endpoint_policy = b.assigned_policies
ORDER BY b.logical_profile ASC
