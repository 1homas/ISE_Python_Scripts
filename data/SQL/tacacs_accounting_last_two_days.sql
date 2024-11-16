--
-- tacacs_accounting_last_two_days
--
-- 💡 Un/Comment columns to quickly customize queries. Remember the last SELECT column must not end with a `,`.
--

SELECT
    * -- all columns
FROM tacacs_accounting_last_two_days
ORDER BY logged_time ASC -- first/oldest records
-- ORDER BY logged_time DESC -- most recent records
FETCH FIRST 10 ROWS ONLY -- limit default number of rows returned for large datasets