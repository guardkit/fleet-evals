language dcl 1.0

actor ApiClient is system

shape UptimeRequest {
  method: Text required
}

event UptimeReported is {
  service: Text required
  started_at: DateTime required
  uptime_seconds: Number required
}

effect LogUptimeQuery is invocation

policy UptimePolicy {
  reliability {
    timeout 1 second
  }
}

capability GetUptime {
  intent UptimeRequest from ApiClient

  outcomes {
    UptimeReturned
  }

  effects {
    LogUptimeQuery
  }

  events {
    emits UptimeReported
  }

  policies {
    UptimePolicy governs capability
    UptimePolicy governs lifecycle
  }

  observe {
    capability duration as uptime_duration
  }

  when {
    otherwise then UptimeReturned
  }

  lifecycle {
    begin Pending
    step Processing
    end Completed
    move Pending to Completed on outcome UptimeReturned
  }
}