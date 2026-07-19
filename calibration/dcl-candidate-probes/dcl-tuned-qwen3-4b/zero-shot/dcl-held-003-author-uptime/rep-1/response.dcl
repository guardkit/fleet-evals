language dcl 1.0

actor Requester is human

shape UptimeRequest {
  method: Method required
}

event UptimeRequested is {
  requester: Requester required
}

outcome UptimeResponse {
  service: Text required
  started_at: DateTime required
  uptime_seconds: Number required
}

policy UptimeReadiness {
  reliability {
    timeout 10 seconds
  }
}

capability GetUptime {
  intent UptimeRequest from Requester

  outcomes {
    UptimeResponse
  }

  rule UptimeRequestMethodIsGet: input.method is "GET"

  effects {
    // No effects — this is a read-only endpoint
  }

  events {
    emits UptimeRequested
  }

  policies {
    UptimeReadiness governs capability
  }

  observe {
    capability duration
    outcome UptimeResponse count as uptime_requests_succeeded
    event UptimeRequested count as uptime_requests_emitted
  }

  when {
    UptimeRequestMethodIsGet violated then UptimeResponse
    otherwise then UptimeResponse
  }

  lifecycle {
    begin Pending
    step Pending
    end Ready
    move Pending to Ready on outcome UptimeResponse
  }
}
