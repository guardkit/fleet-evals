language dcl 1.0

actor Client is system

shape UptimeRequest {}

event UptimeQueried is {
  service: Text required
}

effect FetchUptime is invocation

policy UptimePolicy {
  reliability {
    timeout 500 ms
    idempotency required
  }
  availability {
    degradation allowed
    dependency_tolerance forbidden
  }
}

capability GetUptime {
  intent UptimeRequest from Client

  outcomes {
    UptimeRetrieved
  }

  effects {
    FetchUptime
  }

  events {
    emits UptimeQueried
  }

  policies {
    UptimePolicy governs capability
    UptimePolicy governs effect FetchUptime
    UptimePolicy governs lifecycle
  }

  observe {
    capability duration as uptime_duration
    outcome UptimeRetrieved count as uptime_requests
    effect FetchUptime count failures as uptime_fetch_failures
    lifecycle transitions as uptime_lifecycle_transitions
  }

  when {
    otherwise then UptimeRetrieved
  }

  lifecycle {
    begin Started
    step Active
    end Finished
    move Started to Active on outcome UptimeRetrieved
    move Active to Finished on outcome UptimeRetrieved
  }
}