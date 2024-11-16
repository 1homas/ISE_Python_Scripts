--
-- network_device_groups
--
-- 💡 Un/Comment columns to quickly customize queries. Remember the last SELECT column must not end with a `,`.
--

SELECT
    * -- all columns
    -- id, -- comment
    -- name, -- comment
    -- description, -- comment
    -- created_by, -- comment
    -- create_time, -- comment
    -- update_time, -- comment
    -- active_status -- comment
FROM network_device_groups
ORDER BY name ASC -- alphabetical
FETCH FIRST 10 ROWS ONLY -- limit default number of rows returned for large datasets
