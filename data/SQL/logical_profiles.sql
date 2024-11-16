--
-- 💡 Un/Comment columns to quickly customize queries. Remember the last SELECT column must not end with a `,`.
--

SELECT
    -- * -- all columns
    logical_profile, -- name
    assigned_policies, -- endpoint profile name
    description, -- 
    system_type -- CiscoProvided, etc.
FROM logical_profiles
ORDER BY logical_profile ASC, assigned_policies ASC 
-- FETCH FIRST 10 ROWS ONLY -- limit default number of rows returned for large datasets