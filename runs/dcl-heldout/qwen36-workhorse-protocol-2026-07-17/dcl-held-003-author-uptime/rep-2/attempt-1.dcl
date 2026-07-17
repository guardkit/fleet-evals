language dcl 1.0

actor Client is system

shape UptimeRequest {
  requestId: Uuid required
}

policy UptimeAvailability {
  availability {
    degradation forbidden
  }
}

capability GetUptime {
  intent UptimeRequest from Client

  outcomes {
    UptimeRetrieved
  }

  policies {
    UptimeAvailability governs capability
  }

  observe {
    capability duration as uptime_duration
  }

  when {
    otherwise then UptimeRetrieved
  }

  lifecycle {
    begin step Requested
    end step Completed
    move Requested to Completed on outcome UptimeRetrieved
  }
}