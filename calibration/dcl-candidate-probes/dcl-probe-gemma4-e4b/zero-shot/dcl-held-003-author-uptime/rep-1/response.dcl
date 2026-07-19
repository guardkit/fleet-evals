language dcl 1.0

actor system is system

shape UptimeResponse {
  service: Text required
  started_at: Text required
  uptime_seconds: Decimal required
}

shape UptimeRequest {
  // GET /uptime requires no body input
}

outcome UptimeAvailable
outcome UnsupportedOperation

policy ReadOnlyPolicy {
  // Enforces that the capability is read-only
  constraint mutability is false
}

capability GetUptime {
  intent UptimeRequest from system

  outcomes {
    UptimeAvailable
    UnsupportedOperation
  }

  effects {}

  events {}

  policies {
    ReadOnlyPolicy governs capability
  }

  observe {
    capability duration
    outcome UptimeAvailable count as successful_reads
    outcome UnsupportedOperation count as rejected_reads
  }

  when {
    // If the request attempts a mutating verb, it fails immediately.
    // This models the "Attempting to modify the uptime resource is rejected" requirement.
    input.verb is mutating then UnsupportedOperation
    otherwise then UptimeAvailable
  }

  lifecycle {
    begin Pending
    step Completed
    end Completed
    move Pending to Completed on outcome UptimeAvailable
    move Pending to Completed on outcome UnsupportedOperation
  }
}