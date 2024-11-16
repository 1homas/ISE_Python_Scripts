--
-- ISE Reports > Diagnostics > AAA Diagnostics
--
-- 💡 Un/Comment columns to quickly customize queries. Remember the last SELECT column must not end with a `,`.
--

SELECT
    * -- all columns
    -- timestamp_timezone,
    -- TO_CHAR(timestamp, 'YYYY-MM-DD HH24:MI:SS') AS timestamp, -- drop fractional seconds
    -- session_id,
    -- ise_node,
    -- username,
    -- message_severity,
    -- message_code,
    -- message_text,
    -- category,
    -- info
FROM aaa_diagnostics_view
-- ORDER BY timestamp ASC -- first/oldest records
ORDER BY timestamp DESC -- most recent records
FETCH FIRST 100 ROWS ONLY -- limit default number of rows returned for large datasets
