--
-- 💡 Un/Comment columns to quickly customize queries. Remember the last SELECT column must not end with a `,`.
--

SELECT 
  id, -- Database unique ID
  -- create_time, -- ⚠ not supported in thin mode! TIMESTAMP(6) + TIMEZONE Time when record was created
  -- update_time, -- ⚠ not supported in thin mode! TIMESTAMP(6) + TIMEZONE Time when record was last updated
  policyset_status, -- Specifies if the policy set status is active
  policyset_name, -- Specifies the policy set name
  description -- Specifies the policy sets description
FROM policy_sets
ORDER BY policyset_name ASC
