language dcl 1.0

actor Client is system

shape StatsInput {
}

shape StatsOutput {
  service: Text required
  requests_served: Number required
  first_request_at: DateTime required
}

event StatsRetrieved is {
  service: Text required
  requests_served: Number required
  first_request_at: DateTime required
}

effect ReadStats is tool

policy StatsReliability {
  reliability {
    timeout 5 seconds
  }
  availability {
    degradation forbidden
  }
}

capability GetStats {
  intent StatsInput from Client

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
    StatsReliability governs capability
    StatsReliability governs effect ReadStats
    StatsReliability governs lifecycle
  }

  observe {
    capability duration as stats_duration
    effect ReadStats count failures as read_failures
    outcome StatsReturned count as stats_requests_served
    lifecycle transitions
  }

  when {
    otherwise then StatsReturned
  }

  lifecycle {
    begin Ready
    step Ready
    end Served
    move Ready to Served on outcome StatsReturned
  }
}