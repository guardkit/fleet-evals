language dcl 1.0

actor Service is system

effect RecordRequestCount is persistence
effect RecordFirstRequestTime is persistence

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
  // No input fields; this is a read-only endpoint
}

event StatsUpdated is {
  service: Text required
  requests_served: Integer required
  first_request_at: DateTime required
}

capability GetStats {
  intent StatsRequest from Service

  outcomes {
    StatsResponse
  }

  effects {
    RecordRequestCount
    RecordFirstRequestTime
  }

  events {
    emits StatsUpdated
  }

  policies {
    StatsReliability governs capability
    StatsReliability governs effect RecordRequestCount
    StatsReliability governs effect RecordFirstRequestTime
    StatsReliability governs lifecycle
  }

  observe {
    capability duration
    outcome StatsResponse count as stats_requests_served
    event StatsUpdated count as stats_updates_emitted
    lifecycle transitions
  }

  when {
    // No conditions to trigger outcomes; the outcome is always StatsResponse
    otherwise then StatsResponse
  }

  lifecycle {
    begin Pending
    step Pending
    step Active
    end Active
    // No transitions required since the endpoint is read-only and state is process-lifetime
    // The lifecycle remains active after first request
    move Pending to Active on outcome StatsResponse
  }
}