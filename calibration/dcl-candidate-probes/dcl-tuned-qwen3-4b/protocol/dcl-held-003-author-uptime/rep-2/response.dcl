language dcl 1.0

actor Requester is human

shape UptimeRequest {
  // No fields — this is a read-only endpoint
}

event UptimeResponseSent is {
  service: Text required
  started_at: DateTime required
  uptime_seconds: Number required
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
    UptimeProvided
  }

  rules {
    // No rules — the endpoint is read-only
  }

  effects {
    PersistUptime
  }

  events {
    emits UptimeResponseSent
  }

  policies {
    UptimeReliability governs capability
  }

  observe {
    capability duration as uptime_request_duration
  }

  lifecycle {
    begin step Started
    end step Completed
    step Started {
      kind active
    }
    move Started to Completed on outcome UptimeProvided
  }

  when {
    otherwise then UptimeProvided
  }
}
