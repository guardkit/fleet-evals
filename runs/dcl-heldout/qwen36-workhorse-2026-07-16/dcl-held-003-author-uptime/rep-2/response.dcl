language dcl 1.0

actor Client is system
effect ComputeUptime is computation
policy UptimePolicy {
  reliability {
    retry {
      attempts 1
      backoff linear
    }
    idempotency required
    timeout 5 seconds
  }
}
shape UptimeRequest {
  method: Text required
}
event UptimeReported is {
  service: Text required
  started_at: Text required
  uptime_seconds: Number required
}
capability GetUptime {
  intent UptimeRequest from Client

  outcomes {
    UptimeRetrieved
    MethodRejected
  }

  rule ReadOnly: input.method is "GET"

  effects {
    ComputeUptime
  }

  events {
    emits UptimeReported
  }

  policies {
    UptimePolicy governs capability
    UptimePolicy governs effect ComputeUptime
    UptimePolicy governs lifecycle
  }

  observe {
    capability duration
    outcome UptimeRetrieved count as uptime_requests
    lifecycle transitions
  }

  when {
    ReadOnly violated then MethodRejected
    otherwise then UptimeRetrieved
  }

  lifecycle {
    begin Pending
    step Processing
    end Served
    end Rejected
    move Pending to Processing on outcome UptimeRetrieved
    move Pending to Rejected on outcome MethodRejected
    move Processing to Served on event UptimeReported
  }
}