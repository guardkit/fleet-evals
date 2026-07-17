language dcl 1.0

actor Client is system

shape StatsInput {}

shape StatsResponse {
  service: Text required
  requests_served: Number required
  first_request_at: DateTime
}

event StatsRetrieved is {
  service: Text required
  requests_served: Number required
  first_request_at: DateTime
}

policy StatsAvailability {
  availability {
    degradation forbidden
    dependency_tolerance forbidden
  }
}

capability GetStats {
  intent StatsInput from Client

  outcomes {
    StatsReturned
  }

  events {
    emits StatsRetrieved
  }

  policies {
    StatsAvailability governs capability
    StatsAvailability governs lifecycle
  }

  observe {
    capability duration
    outcome StatsReturned count as stats_requests_served
  }

  when {
    otherwise then StatsReturned
  }

  lifecycle {
    begin step Pending
    step Processing
    end step Completed
    move Pending to Completed on outcome StatsReturned
  }
}