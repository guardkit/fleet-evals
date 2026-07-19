language dcl 1.0

actor Service is system

shape UptimeRequest {
  // No input required for a read-only GET endpoint
}

event UptimeRequested is {
  // No payload needed; request is read-only
}

effect ComputeUptime is persistence

capability GetUptime {
  intent UptimeRequest from Service

  outcomes {
    UptimeResponse
  }

  effects {
    ComputeUptime
  }

  events {
    emits UptimeRequested
  }

  policies {
    reliability {
      timeout 10 seconds
      idempotency required
    }
    reliability governs capability
    reliability governs effect ComputeUptime
  }

  observe {
    capability duration as uptime_query_duration
    effect ComputeUptime count failures as uptime_computation_failures
    outcome UptimeResponse count as uptime_responses_served
  }

  lifecycle {
    begin step Ready
    end step Served
    step Ready {
      kind active
    }
    move Ready to Served on outcome UptimeResponse
  }

  when {
    otherwise then UptimeResponse
  }
}