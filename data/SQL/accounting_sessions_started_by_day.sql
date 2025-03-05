--
-- Accounting Sessions Started by Day
--
-- Author: Thomas Howard, thomas@cisco.com
-- License: MIT - https://mit-license.org
--

SELECT
    TO_CHAR(timestamp, 'YYYY-MM-DD') AS timestamp, -- drop fractional seconds
    COUNT(*) AS starts
FROM radius_accounting
WHERE acct_status_type = 'Start'
GROUP BY TO_CHAR(timestamp, 'YYYY-MM-DD')
ORDER BY timestamp ASC
