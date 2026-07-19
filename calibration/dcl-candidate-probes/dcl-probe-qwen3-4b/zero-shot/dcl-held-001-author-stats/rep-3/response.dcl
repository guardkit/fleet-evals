language dcl 1.0

actor ServiceMonitor is system

effect RecordRequestCount is persistence
effect LogFirstRequestTime is logging

policy StatsReliability {
  reliability {
    retry {
      attempts 0
    }
    idempotency required
    timeout 10 seconds
  }
}

shape StatsRequest {
  // No input; this is a read-only endpoint
}

event RequestCountUpdated is {
  count: Integer required
}

capability GetStats {
  intent StatsRequest from ServiceMonitor

  outcomes {
    StatsResponse
  }

  rule RequestCountUpdated: true

  effects {
    RecordRequestCount
    LogFirstRequestTime after RecordRequestCount
  }

  events {
    emits RequestCountUpdated
  }

  policies {
    StatsReliability governs capability
    StatsReliability governs effect RecordRequestCount
    StatsReliability governs lifecycle
  }

  observe {
    capability duration
    outcome StatsResponse count as stats_responses_served
    effect RecordRequestCount count as request_counts_recorded
    lifecycle transitions
  }

  when {
    RequestCountUpdated then StatsResponse
    otherwise then StatsResponse
  }

  lifecycle {
    begin Active
    step Active
    end Active
    move Active to Active on outcome StatsResponse
  }
}