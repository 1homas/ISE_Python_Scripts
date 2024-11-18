--
-- failure_code_cause
--

SELECT
    * -- all columns
FROM failure_code_cause
FETCH FIRST 10 ROWS ONLY -- limit default number of rows returned for large datasets
