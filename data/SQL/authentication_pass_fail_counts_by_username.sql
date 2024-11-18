--
-- Author: Thomas Howard, thomas@cisco.com
-- License: MIT - https://mit-license.org
--

SELECT
    username,
    COUNT( CASE WHEN passed = 'Pass' THEN 1 END ) AS passed,
    COUNT( CASE WHEN passed = 'Fail' THEN 1 END ) AS failed,
    COUNT(*) AS total
FROM radius_authentications
GROUP BY username
ORDER BY username ASC
FETCH FIRST 50 ROWS ONLY -- limit default number of rows returned for large datasets
