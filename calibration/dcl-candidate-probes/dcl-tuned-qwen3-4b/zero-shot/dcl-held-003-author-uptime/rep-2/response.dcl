language dcl 1.0

actor Requester is human

shape UptimeRequest {
  service: Text required
}

event UptimeRequested is {
  service: Text required
}

outcome UptimeResponse {
  service: Text required
  started_at: Text required
  uptime_seconds: Number required
}

policy UptimeReadonly {
  reliability {
    timeout 10 seconds
  }
}

capability GetUptime {
  intent UptimeRequest from Requester

  outcomes {
    UptimeResponse
  }

  rule UptimeStable: input.service is not null

  effects {
    // No effects needed for read-only endpoint
  }

  events {
    emits UptimeRequested
  }

  policies {
    UptimeReadonly governs capability
  }

  observe {
    capability duration
    outcome UptimeResponse count as uptime_responses
    event UptimeRequested count as uptime_requests
  }

  when {
    UptimeStable violated then UptimeResponse
    otherwise then UptimeResponse
  }

  lifecycle {
    begin Pending
    step Pending
    end Ready
    move Pending to Ready on outcome UptimeResponse
  }
}
