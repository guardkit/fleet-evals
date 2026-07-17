language dcl 1.0

actor Client is system

shape StatsRequest {}

event StatsRetrieved is {
  service: Text required
  requests_served: Number required
  first_request_at: DateTime required
}

effect ReadStats is tool

policy StatsAvailability {
  availability {
    degradation forbidden
    dependency_tolerance forbidden
  }
}

capability GetStats {
  intent StatsRequest from Client

  outcomes {
    StatsReturned
  }

  effects {
    ReadStats
  }

  events {
    emits StatsRetrieved
  }

  policies {
    StatsAvailability governs capability
    StatsAvailability governs effect ReadStats
    StatsAvailability governs lifecycle
  }

  observe {
    capability duration as get_stats_duration
    outcome StatsReturned count as stats_requests
  }

  when {
    otherwise then StatsReturned
  }

  lifecycle {
    begin Pending
    step Active
    end Done
    move Pending to Active on outcome StatsReturned
    move Active to Done on outcome StatsReturned
  }
}