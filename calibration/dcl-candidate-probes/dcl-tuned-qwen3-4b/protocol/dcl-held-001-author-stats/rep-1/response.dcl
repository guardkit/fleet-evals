language dcl 1.0

actor ApiTest is system

shape StatsRequest {
  // No input fields — this is a GET request
}

event StatsFetched is {
  service: Text required
  requests_served: Number required
  first_request_at: DateTime
}

effect PersistStats is persistence

policy StatsReliability {
  reliability {
    timeout 30 seconds
    idempotency required
  }
}

capability GetStats {
  intent StatsRequest from ApiTest

  outcomes {
    StatsFetched
  }

  rules {
    // No rules needed — just a read-only endpoint
  }

  effects {
    PersistStats
  }

  events {
    emits StatsFetched
  }

  policies {
    StatsReliability governs capability
    StatsReliability governs effect PersistStats
  }

  observe {
    capability duration as get_stats_duration
    effect PersistStats count failures as persist_stats_failures
  }

  lifecycle {
    begin step Started
    end step Completed
    step Started {
      kind active
    }
    move Started to Completed on outcome StatsFetched
  }

  when {
    otherwise then StatsFetched
  }
}
