--
-- openapi_operations
--
-- 💡 Un/Comment columns to quickly customize queries. Remember the last SELECT column must not end with a `,`.
--

SELECT
    -- * -- all columns
    logged_at AS timestamp, -- timestamp
    -- request_time -- ⚠ TIMESTAMP(6) WITH TIME ZONE not supported in thin mode
    administrator, -- username
    client_ip,
    server, -- ISE PPAN
    http_method as method, -- [DELETE, GET, PATCH, PUT, POST]
    http_code AS status, -- HTTP numeric status code
    http_status, -- ⚠ text, not status code
    -- request_body, -- ⚠ may contain JSON and may be very large!
    -- request_id,
    request_name, -- URL of API endpoint
    response_duration AS time, -- milliseconds
    error_message AS error,
    message_text AS text -- ?
    -- response, -- ⚠ contains the JSON response and may be very large!
FROM openapi_operations
ORDER BY timestamp ASC -- first/oldest records
-- ORDER BY timestamp DESC -- most recent records
FETCH FIRST 10 ROWS ONLY -- limit default number of rows returned for large datasets
