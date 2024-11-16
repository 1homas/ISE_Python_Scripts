--
-- Endpoint Profiles (profiling_policies)
--
-- 💡 Un/Comment columns to quickly customize queries. Remember the last SELECT column must not end with a `,`.
--

SELECT
    * -- all columns
    -- profiling_policy_name, -- Name of Profiling Policy
    -- description, -- Description of Profiling Policy
FROM profiling_policies
ORDER BY profiling_policy_name ASC -- first/oldest records
-- FETCH FIRST 10 ROWS ONLY -- limit default number of rows returned for large datasets
