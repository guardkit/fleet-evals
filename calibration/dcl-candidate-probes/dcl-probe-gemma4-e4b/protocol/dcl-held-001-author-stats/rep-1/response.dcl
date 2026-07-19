language dcl 1.0

actor api_test is system

shape StatsResponse {
  service: Text required
  requests_served: Number required
  first_request_at: DateTime required
}

outcome StatsAvailable is StatsResponse

policy ServiceAvailability {
  availability {
    dependency_tolerance allowed
  }
}

capability GetStats {
  intent from api_test

  outcomes {
    StatsAvailable
  }

  effects {}

  events {}

  policies {
    ServiceAvailability governs capability
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