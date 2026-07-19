language dcl 1.0

actor ApiTest is system

shape StatsRequest {
  // No input fields; this is a GET endpoint
}

event StatsRequestProcessed is {
  service: Text required
  requests_served: Integer required
  first_request_at: Text required
}

outcome StatsResponse is {
  service: Text required
  requests_served: Integer required
  first_request_at: Text required
}

policy StatsEndpointReliability {
  reliability {
    timeout 30 seconds
    idempotency required
  }
}

capability ApiTestStats {
  intent StatsRequest from ApiTest

  outcomes {
    StatsResponse
  }

  rule RequestsServedIncreases: input.requests_served is not null and input.requests_served >= 0

  effects {
    // No effects; this is a read-only endpoint
  }

  events {
    emits StatsRequestProcessed
  }

  policies {
    StatsEndpointReliability governs capability
  }

  observe {
    capability duration
    outcome StatsResponse count as stats_responses
    lifecycle transitions
  }

  when {
    RequestsServedIncreases violated then StatsResponse
    otherwise then StatsResponse
  }

  lifecycle {
    begin Pending
    step Pending
    end Ready
    move Pending to Ready on outcome StatsResponse
  }
}
