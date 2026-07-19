language dcl 1.0

actor Service is system

shape UptimeRequest {
  // No input required for read-only GET /uptime
}

event UptimeRequested is {
  // No payload needed for read-only request
}

effect ComputeUptime is persistence

capability GetUptime {
  intent UptimeRequest from Service

  outcomes {
    UptimeResponse
  }

  rules {
    // No rules needed for read-only endpoint
  }

  effects {
    ComputeUptime
  }

  events {
    emits UptimeRequested
  }

  policies {
    // No policy needed as the endpoint is read-only and has no reliability or availability concerns
    // However, we include a minimal reliability policy to ensure the capability is properly governed
    reliability {
      timeout 10 seconds
      idempotency required
    }
    governs capability
    governs effect ComputeUptime
    governs lifecycle
  }

  observe {
    capability duration as uptime_query_duration
    effect ComputeUptime count failures as uptime_computation_failures
    lifecycle transitions
  }

  when {
    otherwise then UptimeResponse
  }

  lifecycle {
    begin step Ready
    end step Ready
    // No transitions needed as the capability is stateless and always available
  }
}