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

outcome UptimeDataAvailable {
  // Outcome indicating successful retrieval of uptime data
}

capability GetUptime {
  intent UptimeRequest from ApiTestService

  outcomes {
    UptimeDataAvailable
  }

  rule UptimeValid: input.uptime_seconds >= 0
  rule UptimeIncreases: input.uptime_seconds > previous_input.uptime_seconds

  effects {
    // No effects for read-only endpoint
  }

  events {
    emits UptimeResponseSent
  }

  policies {
    // No policy needed for read-only endpoint; default reliability is sufficient
    // Policy governs lifecycle and outcome observation
    reliability {
      retry {
        attempts 0
        backoff none
      }
      idempotency required
      timeout 10 seconds
    } governs capability
    reliability governs event UptimeResponseSent
  }

  observe {
    capability duration
    outcome UptimeDataAvailable count as uptime_requests_succeeded
    event UptimeResponseSent count as uptime_responses_sent
    lifecycle transitions
  }

  when {
    UptimeValid violated then UptimeDataAvailable
    UptimeIncreases violated then UptimeDataAvailable
    otherwise then UptimeDataAvailable
  }

  lifecycle {
    begin Pending
    step Pending
    step Ready
    end Ready
    move Pending to Ready on outcome UptimeDataAvailable
  }
}