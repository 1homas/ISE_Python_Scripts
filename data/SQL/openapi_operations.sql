SELECT 
  logged_at,
  -- request_time -- ⚠ TIMESTAMP(6) WITH TIME ZONE not supported in thin mode
  administrator,
  client_ip,
  server,
  http_method,
  http_code, -- HTTP numeric status code
  http_status, -- ⚠ text, not status code
  -- request_body, -- ⚠ may contain JSON and may be very large!
  -- request_id,
  request_name, -- URL of API endpoint
  response_duration
  error_message,
  message_text -- ?
  -- response, -- ⚠ contains the JSON response and may be very large!
FROM openapi_operations
-- FETCH FIRST 1 ROWS ONLY
