language dcl 1.0

actor Client is system

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
    MethodNotAllowed
  }

  rule GetOnly: input.method is "GET"

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
    outcome UptimeRetrieved count as uptime_requests
    effect ComputeUptime count failures as uptime_computation_failures
    lifecycle transitions
  }

  when {
    GetOnly violated then MethodNotAllowed
    ComputeUptime unresolved then MethodNotAllowed
    otherwise then UptimeRetrieved
  }

  lifecycle {
    begin Ready
    step Processing
    end Served
    end Failed
    move Ready to Processing on outcome MethodNotAllowed
    move Processing to Served on event UptimeReported
    move Ready to Failed on outcome MethodNotAllowed
  }
}