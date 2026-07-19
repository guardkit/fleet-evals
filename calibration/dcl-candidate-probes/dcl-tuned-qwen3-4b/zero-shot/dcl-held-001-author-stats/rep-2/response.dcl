language dcl 1.0

actor ApiTest is system

shape StatsRequest {
  service: Text required
}

event StatsRequestReceived is {
  service: Text required
}

outcome StatsResponse is {
  service: Text required
  requests_served: Integer required
  first_request_at: DateTime required
}

policy StatsReadonly {
  security {
    allow {
      method GET
    }
    deny {
      method POST
    }
  }
}

shape StatsResponseShape {
  service: Text required
  requests_served: Integer required
  first_request_at: DateTime required
}

capability ApiTestStats {
  intent StatsRequest from ApiTest

  outcomes {
    StatsResponse
  }

  rule FirstRequestSet: input.service is not null

  effects {
    // No effects — this is a read-only endpoint
  }

  events {
    emits StatsRequestReceived
  }

  policies {
    StatsReadonly governs capability
  }

  observe {
    capability duration
    outcome StatsResponse count as stats_responses
  }

  when {
    FirstRequestSet violated then StatsResponse
    otherwise then StatsResponse
  }

  lifecycle {
    begin Inactive
    step Inactive
    step Active
    end Active
    move Inactive to Active on outcome StatsResponse
  }
}
