SELECT table_name,
  column_name
FROM all_tab_columns
WHERE table_name = 'RADIUS_AUTHENTICATIONS'
ORDER BY column_name ASC