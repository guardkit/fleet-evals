language dcl 1.0

actor ApiTestService is system

shape StatsRequest {
  // No input required; this is a read-only endpoint
}

event StatsUpdated is {
  requestsServed: Integer required
  firstRequestAt: Text required
}

outcome StatsResponse {
  service: Text required
  requestsServed: Integer required
  firstRequestAt: Text optional
}

policy StatsReadiness {
  reliability {
    timeout 10 seconds
    idempotency required
    retry {
      attempts 1
      backoff constant
    }
  }
}

capability GetStats {
  intent StatsRequest from ApiTestService

  outcomes {
    StatsResponse
  }

  effects {
    // No effects; the endpoint is read-only
  }

  events {
    emits StatsUpdated
  }

  policies {
    StatsReadiness governs capability
    StatsReadiness governs event StatsUpdated
  }

  observe {
    capability duration
    outcome StatsResponse count as stats_requests_served
    event StatsUpdated count as stats_updates_emitted
  }

  when {
    // No conditions; the endpoint always returns valid stats
    otherwise then StatsResponse
  }

  lifecycle {
    begin Active
    step Active
    end Active
    // Lifecycle is stable; no transitions needed
  }
}