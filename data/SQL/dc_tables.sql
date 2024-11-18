--
-- Lists all available table views in ISE Data Connect 
--
-- Author: Thomas Howard, thomas@cisco.com
-- License: MIT - https://mit-license.org
--

SELECT DISTINCT table_name
FROM all_tab_columns
ORDER BY table_name