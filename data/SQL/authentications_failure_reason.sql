SELECT failure_reason,
  COUNT(*) as total
FROM radius_authentications
GROUP BY failure_reason
ORDER BY failure_reason
-- FETCH FIRST 10 ROWS ONLY