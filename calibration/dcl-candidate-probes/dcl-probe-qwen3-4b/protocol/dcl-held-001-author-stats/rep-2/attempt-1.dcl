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
    backoff exponential
  }
}

capability GetStats {
  intent StatsRequest from Service

  outcomes {
    StatsResponseProvided
  }

  effects {
    UpdateRequestCount
    RecordFirstRequestTime
  }

  events {
    emits StatsRequested
  }

  policies {
    StatsReliability governs capability
    StatsReliability governs effect UpdateRequestCount
    StatsReliability governs effect RecordFirstRequestTime
    StatsReliability governs lifecycle
  }

  observe {
    capability duration as stats_query_duration
    effect UpdateRequestCount count failures as request_count_failures
    effect RecordFirstRequestTime count failures as first_request_time_failures
    lifecycle transitions
  }

  when {
    otherwise then StatsResponseProvided
  }

  lifecycle {
    begin Pending
    step Pending
    step StatsReady waits for event StatsRequested
    end Ready
    end Failed
    move Pending to Ready on outcome StatsResponseProvided
    move Pending to Failed on outcome StatsResponseProvided
  }
}