language dcl 1.0

actor ApiTest is system

shape StatsRequest {
  // No input — this is a GET endpoint
}

event StatsRequested is {
  // No payload
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
    StatsResponse
  }

  rules {
    // No rules — this is a read-only endpoint
  }

  effects {
    PersistStats
  }

  events {
    emits StatsRequested
  }

  policies {
    StatsReliability governs capability
  }

  observe {
    capability duration as get_stats_duration
  }

  when {
    otherwise then StatsResponse
  }

  lifecycle {
    begin step Started
    end step Completed
    step Started {
      kind active
    }
    move Started to Completed on outcome StatsResponse
  }
}
