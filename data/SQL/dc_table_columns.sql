--
-- Shows all columns definitions in the specified ISE Data Connect table.
-- This is similar to doing a `SELECT * FROM {table_name}
--
-- 💡 Un/Comment columns to quickly customize queries. Remember the last SELECT column must not end with a `,`.
--
-- Author: Thomas Howard, thomas@cisco.com
-- License: MIT - https://mit-license.org
--

SELECT
  -- * -- all columns
  table_name, -- 
  column_name, -- 
  data_type, -- 
  data_length, -- 
  char_length, -- 
  -- data_default, -- empty
  -- avg_col_len, -- empty
  -- char_col_decl_length, -- 
  -- char_used, -- 
  -- character_set_name, -- 
  -- collation, -- 
  -- column_id, -- 
  -- data_precision, -- 
  -- data_scale, -- 
  -- data_type_mod, -- 
  -- data_type_owner, -- 
  -- data_upgraded, -- 
  -- default_length, -- 
  -- default_on_null, -- 
  -- density, -- empty
  -- evaluation_edition, -- 
  -- global_stats, -- 'NO'
  -- high_value, -- 
  -- histogram, -- 'NONE'
  -- identity_column, -- 'NO'
  -- last_analyzed, -- 
  -- low_value, -- empty
  -- num_buckets, -- 
  -- num_distinct, -- empty
  -- num_nulls, -- empty
  -- owner, -- 
  -- sample_size, -- empty
  -- unusable_before, -- 
  -- unusable_beginning, -- 
  -- user_stats, -- 
  -- v80_fmt_image, -- 
  nullable -- 
FROM all_tab_columns
WHERE table_name = UPPER('radius_authentications') -- ⚠ must be uppercase to match table name
ORDER BY
  table_name ASC,
  column_name ASC