-- ISE Reports > Audit > Change Configuration Audit Report
SELECT
  timestamp              , -- Time when record added (TIMESTAMP(6))
  admin_name             , -- Name of the admin who made config change
  details                , -- Details of the event
  event                  , -- Config change done
  failure_flag           , -- Failure flag
  host_id                , -- Hostname of ISE node on which change is done
  id                     , -- Database unique ID
  interface              , -- Interface used for login GUI/CLI
  ise_node               , -- Hostname of ISE node
  applied_to_acs_instance, -- ISE nodes to which change is applied
  local_mode             , -- Local mode
  message_class          , -- Message class
  message_code           , -- Message code
  modified_properties    , -- Modified properties
  nas_ip_address         , -- IP address of NAD
  nas_ipv6_address       , -- IPV6 address of NAD
  operation_message_text , -- Operation details
  request_response_type  , -- Type of request response
  requested_operation    , -- Operation done
  object_id              , -- Object ID
  object_name            , -- Name of object for which config is changed
  object_type            -- Type of object for which config is changed
  -- timestamp_timezone  -- Time with timezone when record added (⚠ TIMESTAMP(6)+TZ)
FROM change_configuration_audit
-- FETCH FIRST 10 ROWS ONLY