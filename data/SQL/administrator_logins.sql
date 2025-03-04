--
-- administrator_logins
--
-- 💡 Un/Comment columns to quickly customize queries. Remember the last SELECT column must not end with a `,`.
--

SELECT
    -- * -- all columns
    TO_CHAR(timestamp, 'YYYY-MM-DD HH24:MI:SS') AS timestamp, -- drop fractional seconds
    ip_address, -- comment
    admin_name, -- comment
    admin_session, -- [AdminGUI_Session, ?]
    CASE WHEN LENGTH(event_details) > 40 THEN SUBSTR(event_details, 1, 39) || '...' ELSE event_details END AS event_details, -- trim verbose messages
    -- event_details, -- comment
    event -- comment
    -- timestamp_timezone, -- comment
    -- ise_node, -- comment
    -- ipv6_address, -- comment
    -- interface, -- [GUI, ERS]
FROM administrator_logins
WHERE admin_name = 'readonly'
-- WHERE admin_name = 'iseadamin'
ORDER BY timestamp ASC -- first/oldest records
-- ORDER BY timestamp DESC -- most recent records
FETCH FIRST 100 ROWS ONLY -- limit default number of rows returned for large datasets