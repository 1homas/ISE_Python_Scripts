--
-- Author: Thomas Howard, thomas@cisco.com
-- License: MIT - https://mit-license.org
--

SELECT
    MAX(timestamp) AS timestamp,
    username
FROM radius_authentications
-- WHERE username = 'thomas'
GROUP BY username
ORDER BY username ASC
FETCH FIRST 50 ROWS ONLY -- limit default number of rows returned for large datasets
