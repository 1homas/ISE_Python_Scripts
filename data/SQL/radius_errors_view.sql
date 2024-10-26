SELECT message_code as error,
  COUNT(*) AS count,
  MAX(message_text) AS message_text
FROM radius_errors_view
GROUP BY message_code
ORDER BY count DESC
-- FETCH FIRST 10 ROWS ONLY