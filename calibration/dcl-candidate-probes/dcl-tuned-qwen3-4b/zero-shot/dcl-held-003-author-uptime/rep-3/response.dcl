language dcl 1.0

actor ApiTest is system

effect ReturnUptime is response

shape UptimeRequest {
  method: Method required
  path: Path required
}

event UptimeRequested is {
  method: Method required
  path: Path required
}

outcome UptimeResponse {
  service: Text required
  started_at: DateTime required
  uptime_seconds: Decimal required
}

policy UptimeReliability {
  reliability {
    timeout 10 seconds
  }
}

capability ApiTestUptime {
  intent UptimeRequest from ApiTest

  outcomes {
    UptimeResponse
  }

  rule UptimeRequest.method is "GET" and UptimeRequest.path is "/uptime"

  effects {
    ReturnUptime
  }

  events {
    emits UptimeRequested
  }

  policies {
    UptimeReliability governs capability
  }

  observe {
    capability duration
    outcome UptimeResponse count as uptime_responses
    lifecycle transitions
  }

  when {
    UptimeRequest.method is not "GET" then UptimeResponse
    UptimeRequest.path is not "/uptime" then UptimeResponse
    otherwise then UptimeResponse
  }

  lifecycle {
    begin Pending
    step Pending
    end Ready
    move Pending to Ready on outcome UptimeResponse
  }
}
