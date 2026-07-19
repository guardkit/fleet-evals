language dcl 1.0

actor Requester is human

shape UptimeRequest {
  // No fields — read-only endpoint
}

event UptimeRequested is {
  // No payload — read-only endpoint
}

effect PersistUptime is persistence

policy UptimeReliability {
  reliability {
    timeout 30 seconds
    idempotency required
  }
}

capability GetUptime {
  intent UptimeRequest from Requester

  outcomes {
    UptimeResponse
  }

  rule UptimeValid: uptime_seconds >= 0
  rule UptimeIncreases: uptime_seconds > previous_uptime_seconds

  effects {
    PersistUptime
  }

  events {
    emits UptimeRequested
  }

  policies {
    UptimeReliability governs capability
  }

  observe {
    capability duration as get_uptime_duration
  }

  when {
    UptimeValid violated then UptimeResponse
    otherwise then UptimeResponse
  }

  lifecycle {
    begin Pending
    step Pending
    end Completed
    move Pending to Completed on outcome UptimeResponse
  }
}
