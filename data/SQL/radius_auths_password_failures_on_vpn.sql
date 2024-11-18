-- Query to determine if there is a credential stuffing attack occurring via VPN
SELECT username,
  nas_port_type,
  failure_reason,
  COUNT(
    CASE
      WHEN failed = '1' THEN 1
    END
  ) AS failed,
  COUNT(*) AS total
FROM radius_authentications
WHERE nas_port_type = 'Virtual'
  and failure_reason = '22040 Wrong password or invalid shared secret'
GROUP BY username,
  nas_port_type,
  failure_reason