--
-- security_groups
--
-- 💡 Un/Comment columns to quickly customize queries. Remember the last SELECT column must not end with a `,`.
--

SELECT
    * -- all columns
    -- name,
    -- sgt_dec,
    -- sgt_hex,
    -- description,
    -- learned_from
FROM security_groups
ORDER BY name ASC -- alphabetical
-- ORDER BY sgt_dec ASC -- numerical
-- ORDER BY sgt_dec DESC -- numerical
