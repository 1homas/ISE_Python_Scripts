--
-- ISE Reports > Diagnostics > AAA Diagnostics
--
-- Author: Thomas Howard, thomas@cisco.com
-- License: MIT - https://mit-license.org
--

SELECT
    -- timestamp_timezone,
    TO_CHAR(timestamp, 'YYYY-MM-DD HH24:MI:SS') AS timestamp, -- drop fractional seconds
    session_id, -- ise-ppan/520285697/348
    -- ise_node,
    username,
    message_severity AS severity,
    message_code AS msg_code,
    message_text AS msg_text,
    -- category, -- always CISE_RADIUS_Diagnostics
    info -- RADIUS attribute details
FROM aaa_diagnostics_view
-- ORDER BY timestamp ASC -- first/oldest records
ORDER BY timestamp DESC -- most recent records
FETCH FIRST 10 ROWS ONLY
