language dcl 1.0

actor Client is system

shape StatsRequestInput {
}

shape StatsResponse {
  service: Text required
  requests_served: Number required
  first_request_at: DateTime
}

event StatsQueried is {
  service: Text required
  requests_served: Number required
  first_request_at: DateTime
}

effect ReadStats is tool

policy StatsAvailability {
  availability {
    degradation forbidden
    dependency_tolerance forbidden
  }
}

capability GetStats {
  intent StatsRequestInput from Client

  outcomes {
    StatsRetrieved
  }

  effects {
    ReadStats
  }

  events {
    emits StatsQueried
  }

  policies {
    StatsAvailability governs capability
    StatsAvailability governs effect ReadStats
    StatsAvailability governs lifecycle
  }

  observe {
    capability duration
    outcome StatsRetrieved count as stats_requests
  }

  when {
    otherwise then StatsRetrieved
  }

  lifecycle {
    begin Pending
    step Active
    end Completed
    move Pending to Active on outcome StatsRetrieved
    move Active to Completed on outcome StatsRetrieved
  }
}