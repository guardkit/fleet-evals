language dcl 1.0

actor Client is system

shape UptimeRequest {}

event UptimeReported is {
  service: Text required
  started_at: DateTime required
  uptime_seconds: Number required
}

policy UptimeAvailability {
  availability {
    degradation forbidden
    dependency_tolerance forbidden
  }
}

capability GetUptime {
  intent UptimeRequest from Client

  outcome UptimeRetrieved

  events {
    emits UptimeReported
  }

  policies {
    UptimeAvailability governs capability
    UptimeAvailability governs lifecycle
  }

  observe {
    capability duration as uptime_duration
    outcome UptimeRetrieved count as uptime_requests
  }

  when {
    otherwise then UptimeRetrieved
  }

  lifecycle {
    begin step Requested
    end step Completed
    move Requested to Completed on outcome UptimeRetrieved
  }
}