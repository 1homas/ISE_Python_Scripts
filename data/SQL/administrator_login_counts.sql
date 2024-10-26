SELECT MAX(timestamp),
  MAX(ise_node),
  admin_name,
  COUNT(admin_name) AS count,
  --   ip_address,
  --   ipv6_address,
  --   interface,
  MAX(admin_session),
  MAX(event_details) event
FROM administrator_logins
GROUP BY admin_name
ORDER BY count DESC