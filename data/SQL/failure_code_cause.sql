--
-- failure_code_cause
-- 💡 Un/Comment columns to quickly customize queries. Remember the last SELECT column must not end with a `,`.
--

SELECT
    -- * -- all columns
    failure_code, -- the failure code
    -- CASE WHEN LENGTH(failure_code) > 50 THEN SUBSTR(failure_code, 1, 49) || '...' ELSE failure_code END AS failure_code, -- trim verbose messages
    failure_cause -- the failure cause
    -- CASE WHEN LENGTH(failure_cause) > 60 THEN SUBSTR(failure_cause, 1, 59) || '...' ELSE failure_cause END AS failure_cause -- trim verbose messages

FROM failure_code_cause
ORDER BY failure_code ASC
-- FETCH FIRST 10 ROWS ONLY -- limit default number of rows returned for large datasets
