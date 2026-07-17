language dcl 1.0

actor Client is system
effect ComputeUptime is persistence
policy UptimePolicy {
  reliability {
    retry {
      attempts 1
      backoff exponential
    }
    idempotency required
    timeout 5 seconds
  }
}
shape UptimeRequest {
  method: Text required
}
event UptimeData is {
  service: Text required
  started_at: Text required
  uptime_seconds: Number required
}
capability GetUptime {
  intent UptimeRequest from Client

  outcomes {
    UptimeReturned
    MethodNotAllowed
  }

  rule ReadOnly: input.method is "GET"

  effects {
    ComputeUptime
  }

  events {
    emits UptimeData
  }

  policies {
    UptimePolicy governs capability
    UptimePolicy governs effect ComputeUptime
    UptimePolicy governs lifecycle
  }

  observe {
    capability duration
    outcome UptimeReturned count as uptime_requests
    effect ComputeUptime count failures as compute_failures
    lifecycle transitions
  }

  when {
    ReadOnly violated then MethodNotAllowed
    otherwise then UptimeReturned
  }

  lifecycle {
    begin Pending
    step Processing
    end Returned
    end Rejected
    move Pending to Returned on outcome UptimeReturned
    move Pending to Rejected on outcome MethodNotAllowed
  }
}