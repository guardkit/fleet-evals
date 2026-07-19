language dcl 1.0

actor Service is system

shape StatsRequest {
  // No input; this is a read-only endpoint
}

event StatsRequested is {
  // No payload; request is read-only
}

effect IncrementRequestCount is persistence
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
    // No effects should be triggered on read-only endpoint; the stats are computed in-process
  }

  events {
    emits StatsRequested
  }

  policies {
    StatsReliability governs capability
  }

  observe {
    capability duration as stats_query_duration
    effect IncrementRequestCount count failures as request_count_failures
    effect RecordFirstRequestTime count failures as first_request_time_failures
  }

  lifecycle {
    begin Pending
    step Pending
    step Ready waits for event StatsRequested
    end Ready
    move Pending to Ready on outcome StatsResponseProvided
  }

  when {
    otherwise then StatsResponseProvided
  }
}