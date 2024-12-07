--
-- Last Authentication (max timestamp) by Username
--
-- Author: Thomas Howard, thomas@cisco.com
-- License: MIT - https://mit-license.org
--

SELECT
    TO_CHAR(MAX(timestamp), 'YYYY-MM-DD HH24:MI:SS') AS timestamp, -- drop fractional seconds
    username
FROM radius_authentications
-- WHERE username = 'thomas'
-- WHERE timestamp > sysdate - INTERVAL '10' SECOND -- last N seconds
-- WHERE timestamp > sysdate - INTERVAL '1' MINUTE  -- last N minutes
-- WHERE timestamp > sysdate - INTERVAL '1' HOUR -- last N hours
WHERE timestamp > sysdate - INTERVAL '1' DAY -- last N days
GROUP BY username
ORDER BY username ASC
-- FETCH FIRST 50 ROWS ONLY -- limit default number of rows returned for large datasets
