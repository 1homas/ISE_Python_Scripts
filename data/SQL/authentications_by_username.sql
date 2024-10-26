SELECT username,
  COUNT(*) AS count
FROM radius_authentications
GROUP BY username
ORDER BY count DESC
-- FETCH FIRST 10 ROWS ONLY