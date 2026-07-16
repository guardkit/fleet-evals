language dcl 1.0

actor ApiConsumer is system

shape UptimeRequest {}

outcome UptimeRetrieved

policy UptimeReliability {
  reliability {
    timeout 3 seconds
  }
}

capability GetUptime {
  intent UptimeRequest from ApiConsumer

  outcomes {
    UptimeRetrieved
  }

  effects {}

  events {}

  policies {
    UptimeReliability governs capability
    UptimeReliability governs lifecycle
  }

  observe {
    capability duration
    outcome UptimeRetrieved count as uptime_requests
  }

  when {
    otherwise then UptimeRetrieved
  }

  lifecycle {
    begin Pending
    step Processing
    end Completed
    move Pending to Completed on outcome UptimeRetrieved
  }
}