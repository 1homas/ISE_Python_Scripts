--
-- _____
--

SELECT
    * -- all columns
    -- logged_at,
    -- identity,
    -- time_spent,
    -- logged_in,
    -- logged_out,
    -- endpoint_id,
    -- ip_address,
FROM guest_accounting
ORDER BY logged_at ASC
FETCH FIRST 10 ROWS ONLY -- limit default number of rows returned for large datasets