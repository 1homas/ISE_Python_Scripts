--
-- network_devices
--
-- 💡 Un/Comment columns to quickly customize queries. Remember the last SELECT column must not end with a `,`.
--

SELECT
    * -- all columns
    -- id,
    -- name,
    -- ip_mask,
    -- profile_name,
    -- location,
    -- type
FROM network_devices
-- WHERE type LIKE '%MX%' -- Meraki MX
-- WHERE type LIKE '%mr%' -- Meraki MR
-- WHERE type LIKE '%ms%' -- Meraki MS
ORDER BY name ASC
-- FETCH FIRST 10 ROWS ONLY -- limit default number of rows returned for large datasets
