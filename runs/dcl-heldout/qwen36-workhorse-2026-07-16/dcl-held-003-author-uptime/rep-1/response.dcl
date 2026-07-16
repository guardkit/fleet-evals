language dcl 1.0

actor Client is system

shape UptimeRequest {}

effect ComputeUptime is computation

policy UptimeReliability {
  reliability {
    retry {
      attempts 1
      backoff exponential
    }
    idempotency required
    timeout 5 seconds
  }
}

event UptimeReported is {
  service: Text required
  started_at: Text required
  uptime_seconds: Decimal required
}

capability GetUptime {
  intent UptimeRequest from Client

  outcomes {
    UptimeRetrieved
    MethodNotSupported
  }

  rule ReadOnlyAccess: true

  effects {
    ComputeUptime
  }

  events {
    emits UptimeReported
  }

  policies {
    UptimeReliability governs capability
    UptimeReliability governs effect ComputeUptime
    UptimeReliability governs lifecycle
  }

  observe {
    capability duration
    outcome UptimeRetrieved count as uptime_requests_served
    effect ComputeUptime count failures as uptime_calc_failures
    lifecycle transitions
  }

  when {
    ReadOnlyAccess violated then MethodNotSupported
    otherwise then UptimeRetrieved
  }

  lifecycle {
    begin Pending
    step Processing
    end Served
    end Failed
    move Pending to Served on outcome UptimeRetrieved
    move Pending to Failed on outcome MethodNotSupported
  }
}