--
-- _____
--
-- 💡 Un/Comment columns to quickly customize queries. Remember the last SELECT column must not end with a `,`.
--

SELECT
    * -- all columns
FROM guest_devicelogin_audit
FETCH FIRST 10 ROWS ONLY -- limit default number of rows returned for large datasets