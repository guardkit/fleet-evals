```dcl
language dcl 1.0

actor ApiTestService is system

shape UptimeRequest {
  // No input required for GET /uptime; read-only
}

event UptimeFetched is {
  service: Text required
  started_at: Text required
  uptime_seconds: Number required
}

outcome UptimeResponse {
  service: Text required
  started_at: Text required
  uptime_seconds: Number required
}

capability GetUptime {
  intent UptimeRequest from ApiTestService

  outcomes {
    UptimeResponse
  }

  effects {
    // No effects; read-only endpoint
  }

  events {
    emits UptimeFetched
  }

  policies {
    // No policy needed for read-only endpoint; default reliability is sufficient
    // Policy governs lifecycle and outcomes
    reliability {
      retry {
        attempts 0
      }
      idempotency required
      timeout 10 seconds
    } governs capability
    reliability governs lifecycle
  }

  observe {
    capability duration
    outcome UptimeResponse count as uptime_requests_served
    event UptimeFetched count as uptime_fetched_events
    lifecycle transitions
  }

  when {
    // No conditions to evaluate; always returns UptimeResponse
    otherwise then UptimeResponse
  }

  lifecycle {
    begin Ready
    step Ready
    end Ready
    // No transitions needed; endpoint is always ready
  }
}
```