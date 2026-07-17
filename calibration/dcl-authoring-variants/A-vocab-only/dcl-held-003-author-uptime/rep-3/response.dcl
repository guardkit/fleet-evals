language dcl 1.0

actor ApiClient is system

shape UptimeRequest {
  method: Text required
}

outcome UptimeRetrieved is {
  service: Text required
  started_at: DateTime required
  uptime_seconds: Number required
}

event UptimeQueried is {
  service: Text required
  started_at: DateTime required
  uptime_seconds: Number required
}

policy UptimeReliability {
  reliability {
    timeout 5 seconds
    idempotency required
  }
}

capability GetUptime {
  intent UptimeRequest from ApiClient

  outcomes {
    UptimeRetrieved
  }

  events {
    emits UptimeQueried
  }

  policies {
    UptimeReliability governs capability
  }

  lifecycle {
    begin Pending
    step Processing
    end Complete
    move Pending to Processing on outcome UptimeRetrieved
    move Processing to Complete on outcome UptimeRetrieved
  }

  when {
    otherwise then UptimeRetrieved
  }
}