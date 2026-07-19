language dcl 1.0

shape StatsResponse {
  service: Text required
  requests_served: Number required
  first_request_at: DateTime required
}

actor api_test is system

policy HighAvailability {
  availability {
    dependency_tolerance allowed
  }
}

capability GetStats {
  intent from api_test

  outcomes {
    StatsAvailable is StatsResponse
  }

  effects {}

  events {}

  policies {
    HighAvailability governs capability
  }

  observe {
    capability duration as stats_read_latency
  }

  lifecycle {
    begin Active
    end Active
  }

  when {
    otherwise then StatsAvailable
  }
}