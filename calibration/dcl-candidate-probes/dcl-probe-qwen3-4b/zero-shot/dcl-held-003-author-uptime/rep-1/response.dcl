```dcl
language dcl 1.0

actor ApiTestService is system

shape UptimeRequest {
  // No input required for GET /uptime; it is read-only
}

event UptimeResponseSent is {
  service: Text required
  started_at: Text required
  uptime_seconds: Number required
}

outcome UptimeResponse {
  service: Text required
  started_at: Text required
  uptime_seconds: Number required
}

policy UptimeReadonlyPolicy {
  reliability {
    retry {
      attempts 0
    }
    idempotency required
    timeout 10 seconds
  }
}

capability GetUptime {
  intent UptimeRequest from ApiTestService

  outcomes {
    UptimeResponse
  }

  rule UptimeValid: input.uptime_seconds >= 0

  effects {
    // No effects; this is a read-only endpoint
  }

  events {
    emits UptimeResponseSent
  }

  policies {
    UptimeReadonlyPolicy governs capability
    UptimeReadonlyPolicy governs outcome UptimeResponse
  }

  observe {
    capability duration
    outcome UptimeResponse count as uptime_responses_sent
    event UptimeResponseSent count as uptime_response_sent_events
  }

  when {
    UptimeValid then UptimeResponse
    otherwise then UptimeResponse
  }

  lifecycle {
    begin Ready
    end Ready
    // No transitions needed as the endpoint is always available
  }
}
```