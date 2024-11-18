--
-- RADIUS Authentications by Failure Reason
--
-- Author: Thomas Howard, thomas@cisco.com
-- License: MIT - https://mit-license.org
--

SELECT
  COUNT(*) as total,
  failure_reason
FROM radius_authentications
GROUP BY failure_reason
ORDER BY total DESC
-- FETCH FIRST 10 ROWS ONLY -- limit default number of rows returned for large datasets
