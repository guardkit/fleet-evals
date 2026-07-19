language dcl 1.0

actor ApiTest is system

shape StatsRequest {
  service: Text required
}

event StatsRequested is {
  service: Text required
}

outcome StatsResponse is {
  service: Text required
  requests_served: Integer required
  first_request_at: Text required
}

policy StatsReadonly {
  reliability {
    timeout 30 seconds
  }
}

capability ApiTestStats {
  intent StatsRequest from ApiTest

  outcomes {
    StatsResponse
  }

  rule RequestsServedIncreases: input.requests_served is not null and input.requests_served < output.requests_served

  effects {
  }

  events {
    emits StatsRequested
  }

  policies {
    StatsReadonly governs capability
  }

  observe {
    capability duration
    outcome StatsResponse count as stats_responses
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
