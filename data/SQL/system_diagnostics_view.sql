--
-- system_diagnostics_view
--
-- 💡 Un/Comment columns to quickly customize queries. Remember the last SELECT column must not end with a `,`.
--

SELECT
    * -- all columns
    -- id,
    -- timestamp_timezone,
    -- timestamp,
    -- ise_node,
    -- message_severity,
    -- message_code,
    -- message_text,
    -- category,
    -- diagnostic_info
FROM system_diagnostics_view
ORDER BY timestamp ASC
FETCH FIRST 10 ROWS ONLY -- limit default number of rows returned for large datasets
