language dcl 1.0

actor ApiCaller is system

shape StatsRequest {}

shape StatsResponse {
  service: Text required
  requests_served: Number required
  first_request_at: DateTime required
}

effect ReadStats is invocation

policy StatsAvailability {
  availability {
    degradation forbidden
  }
}

capability GetStats {
  intent StatsRequest from ApiCaller

  outcomes {
    StatsReturned
  }

  effects {
    ReadStats
  }

  policies {
    StatsAvailability governs capability
    StatsAvailability governs lifecycle
  }

  observe {
    capability duration
    outcome StatsReturned count as stats_requests
  }

  when {
    otherwise then StatsReturned
  }

  lifecycle {
    begin Pending
    step Active
    end Completed
    move Pending to Completed on outcome StatsReturned
  }
}