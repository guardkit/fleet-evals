language dcl 1.0

actor Service is system

shape StatsRequest {
  // No input required; this is a read-only endpoint
}

event StatsRequested is {
  // No payload needed; request is read-only
}

effect UpdateRequestCount is persistence
effect RecordFirstRequestTime is persistence

policy StatsReliability {
  reliability {
    timeout 10 seconds
    idempotency required
  }
}

capability GetStats {
  intent StatsRequest from Service

  outcomes {
    StatsResponseProvided
  }

  effects {
    // No effects should be triggered on a read-only endpoint
  }

  events {
    emits StatsRequested
  }

  policies {
    StatsReliability governs capability
    // Remove effect governance as it's not needed and causes redundant policy warnings
  }

  observe {
    capability duration as stats_query_duration
    lifecycle transitions
  }

  when {
    otherwise then StatsResponseProvided
  }

  lifecycle {
    begin Pending
    step Pending
    end Ready
    move Pending to Ready on outcome StatsResponseProvided
  }
}