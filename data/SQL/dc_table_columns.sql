--
-- Shows all columns definitions in the specified ISE Data Connect table.
-- This is similar to doing a `SELECT * FROM {table_name}
--
-- Author: Thomas Howard, thomas@cisco.com
-- License: MIT - https://mit-license.org
--

SELECT
    * -- all columns
    -- table_name,
    -- column_name
FROM all_tab_columns
WHERE table_name = UPPER('radius_authentications') -- ⚠ must be uppercase to match table name
ORDER BY table_name,column_name ASC
