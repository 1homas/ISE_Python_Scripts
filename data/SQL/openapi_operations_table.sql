SELECT 
  logged_at,
  -- request_time -- ⚠ TIMESTAMP(6) WITH TIME ZONE not supported in thin mode
  administrator,
  client_ip,
  server,
  error_message,
  http_code,
  http_method,
  http_status,
  request_body,
  request_id,
  request_name,
  response_duration,
  message_text, -- ?
  response -- ⚠ contains the JSON response and may be very large!
FROM openapi_operations
-- FETCH FIRST 1 ROWS ONLY
