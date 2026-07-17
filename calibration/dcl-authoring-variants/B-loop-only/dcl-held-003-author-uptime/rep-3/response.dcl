language dcl 1.0

actor UptimeRequester is system

effect ComputeUptime is persistence

policy UptimeReliability {
  reliability {
    retry {
      attempts 1
      backoff none
    }
    idempotency required
    timeout 5 seconds
  }
}

shape UptimeInput {
  requestId: Text required
}

event UptimeDataPublished is {
  service: Text required
  started_at: Text required
  uptime_seconds: Number required
}

capability GetUptime {
  intent UptimeInput from UptimeRequester

  outcomes {
    UptimeReturned
  }

  rule ReadOnlyAccess: true

  effects {
    ComputeUptime
  }

  events {
    emits UptimeDataPublished
  }

  policies {
    UptimeReliability governs capability
    UptimeReliability governs effect ComputeUptime
    UptimeReliability governs lifecycle
  }

  observe {
    capability duration
    outcome UptimeReturned count as uptime_requests
  }

  when {
    otherwise then UptimeReturned
  }

  lifecycle {
    begin Pending
    step Processing
    end Ready
    move Pending to Ready on outcome UptimeReturned
  }
}