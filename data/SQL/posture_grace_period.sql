--
-- posture_grace_period
--
-- 💡 Un/Comment columns to quickly customize queries. Remember the last SELECT column must not end with a `,`.
--

SELECT
    * -- all columns
    -- mac_list, -- Specifies the list of MAC address
    -- last_grace_expiry, -- Specifies the posture grace period expiration time
FROM posture_grace_period
-- FETCH FIRST 10 ROWS ONLY -- limit default number of rows returned for large datasets
