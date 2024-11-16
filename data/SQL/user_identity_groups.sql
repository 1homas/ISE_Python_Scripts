--
-- _____
--
-- 💡 Un/Comment columns to quickly customize queries. Remember the last SELECT column must not end with a `,`.
--

SELECT
    * -- all columns
    -- id,
    -- name,
    -- description,
    -- created_by,
    -- create_time,
    -- update_time,
    -- status
FROM user_identity_groups
-- ORDER BY update_time ASC -- first/oldest records
ORDER BY update_time DESC -- most recent records
FETCH FIRST 10 ROWS ONLY -- limit default number of rows returned for large datasets
