language dcl 1.0

actor System is system

shape StatsResponse {
  service: Text required
  requests_served: Number required
  first_request_at: Date required
}

outcome StatsAvailable

policy ReadOnlyAccess {
  availability {
    dependency_tolerance required
  }
}

capability GetStats {
  intent StatsResponse from System

  outcomes {
    StatsAvailable
  }

  effects {}

  events {}

  policies {
    ReadOnlyAccess governs capability
  }

  observe {
    capability duration as stats_retrieval_duration
  }

  lifecycle {
    begin Running
    end Running
    step Running {
      kind active
      deadline 1 second causing outcome StatsAvailable
    }
  }

  when {
    otherwise then StatsAvailable
  }
}