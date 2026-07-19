language dcl 1.0

actor Service is system

shape UptimeResponse {
  service: Text required
  started_at: DateTime required
  uptime_seconds: Number required
}

capability GetUptime {
  intent UptimeRequest from Service

  outcomes {
    UptimeResponse
  }

  effects {
    // No effect needed as the response is read-only and computed directly
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
  }

  observe {
    capability duration as uptime_query_duration
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