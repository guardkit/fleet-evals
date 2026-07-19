language dcl 1.0

actor ApiTest is system

shape UptimeRequest {
  service: Text required
  started_at: DateTime required
  uptime_seconds: Number required
}

event UptimeRequested is {
  service: Text required
}

effect PersistUptime is persistence

policy UptimeReliability {
  reliability {
    timeout 30 seconds
    idempotency required
  }
}

capability GetUptime {
  intent UptimeRequest from ApiTest

  outcomes {
    UptimeProvided
  }

  rules {
    ValidUptime: uptime_seconds >= 0
  }

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
    capability duration as uptime_duration
  }

  when {
    ValidUptime violated then UptimeProvided
    otherwise then UptimeProvided
  }

  lifecycle {
    begin step Started
    end step Completed
    step Started {
      kind active
    }
    move Started to Completed on outcome UptimeProvided
  }
}
