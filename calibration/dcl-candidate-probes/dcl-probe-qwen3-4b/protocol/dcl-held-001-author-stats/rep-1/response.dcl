language dcl 1.0

actor Service is system

shape StatsRequest {
  // No input required; this is a read-only endpoint
}

event StatsRequested is {
  // No payload needed; just a request event
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
    IncrementRequestCount
    RecordFirstRequestTime
  }

  events {
    emits StatsRequested
  }

  policies {
    StatsReliability governs capability
    StatsReliability governs effect IncrementRequestCount
    StatsReliability governs effect RecordFirstRequestTime
    StatsReliability governs lifecycle
  }

  observe {
    capability duration as stats_query_duration
    effect IncrementRequestCount count failures as request_count_failures
    effect RecordFirstRequestTime count failures as first_request_time_failures
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