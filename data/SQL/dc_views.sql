--
-- Lists all available table views in ISE Data Connect 
--
-- Author: Thomas Howard, thomas@cisco.com
-- License: MIT - https://mit-license.org
--

SELECT view_name
FROM user_views
ORDER BY view_name ASC