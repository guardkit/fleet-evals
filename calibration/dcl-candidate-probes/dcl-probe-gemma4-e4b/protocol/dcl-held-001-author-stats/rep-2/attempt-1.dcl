language dcl 1.0

shape StatsResponse {
  service: Text required
  requests_served: Number required
  first_request_at: Date required
}

outcome StatsAvailable

policy StatAvailability {
  availability {
    dependency_tolerance allowed
  }
}

capability GetStats {
  intent StatsResponse

  outcomes {
    StatsAvailable
  }

  effects {}

  events {}

  policies {
    StatAvailability governs capability
  }

  observe {
    capability duration as stats_retrieval_duration
  }

  lifecycle {
    begin Pending
    end Running
    step Pending {
      kind active
      deadline 1 second causing outcome StatsAvailable
    }
    move Pending to Running on outcome StatsAvailable
  }

  when {
    otherwise then StatsAvailable
  }
}