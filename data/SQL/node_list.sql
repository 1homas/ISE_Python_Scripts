--
-- node_list table practical view.
--
-- 💡 Un/Comment columns to quickly customize queries. Remember the last SELECT column must not end with a `,`.
--

SELECT
    hostname,
    node_type,
    node_role,
    active_status,
    pdp_services,
    udi_pid,
    udi_vid,
    udi_sn,
    patch_version,
    vm_info
    -- pic_node,
    -- installation_type,
    -- gateway,
    -- replication_status,
    -- host_alias,
    -- create_time,
    -- update_time,
    -- xgrid_enabled,
    -- xgrid_peer,
    -- udi_pt,
    -- api_node
FROM node_list
ORDER BY hostname ASC
