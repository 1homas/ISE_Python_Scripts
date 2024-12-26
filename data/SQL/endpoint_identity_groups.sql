--
-- endpoint_identity_groups
--

SELECT
    * -- 
    -- id, -- database unique id
    -- name, -- name
    -- description, -- description
    -- created_by, -- username
    -- create_time, -- created TIMESTAMP(6)
    -- update_time, -- updated TIMESTAMP(6)
    -- status -- Active/Inactive
FROM endpoint_identity_groups -- 
ORDER BY name ASC
