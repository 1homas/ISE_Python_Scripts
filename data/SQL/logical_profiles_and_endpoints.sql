SELECT b.logical_profile,
    b.assigned_policies,
    a.mac_address
FROM endpoints_data a,
    logical_profiles b
WHERE a.endpoint_policy = b.assigned_policies