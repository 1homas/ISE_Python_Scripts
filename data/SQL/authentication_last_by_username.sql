SELECT MAX(timestamp) AS timestamp,
  username
FROM radius_authentications
GROUP BY username
ORDER BY username ASC
-- FETCH FIRST 10 ROWS ONLY