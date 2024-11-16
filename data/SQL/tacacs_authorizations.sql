--
-- tacacs_authorizations
--

SELECT
    * -- all columns
FROM tacacs_authorizations
ORDER BY logged_time ASC -- first/oldest records
-- ORDER BY logged_time DESC -- most recent records
FETCH FIRST 10 ROWS ONLY -- limit default number of rows returned for large datasets