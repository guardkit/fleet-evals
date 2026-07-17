language dcl 1.0

actor Requester is system

shape UptimeRequest {}

outcome UptimeRetrieved
outcome MethodNotAllowed

policy UptimeAvailability {
  reliability {
    timeout 5 seconds
  }
  availability {
    degradation allowed
  }
}

capability GetUptime {
  intent UptimeRequest from Requester

  outcomes {
    UptimeRetrieved
    MethodNotAllowed
  }

  rules {
    ReadOnly: true
  }

  policies {
    UptimeAvailability governs capability
    UptimeAvailability governs lifecycle
  }

  observe {
    capability duration as uptime_check_duration
    outcome UptimeRetrieved count as uptime_requests
  }

  when {
    ReadOnly violated then MethodNotAllowed
    otherwise then UptimeRetrieved
  }

  lifecycle {
    begin Active
    step Active
    end Completed
    move Active to Completed on outcome UptimeRetrieved
    move Active to Completed on outcome MethodNotAllowed
  }
}