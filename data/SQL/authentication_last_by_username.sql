SELECT MAX(timestamp) AS timestamp,
  username
FROM radius_authentications
-- WHERE username = 'thomas'
GROUP BY username
ORDER BY username ASC
-- FETCH FIRST 10 ROWS ONLY