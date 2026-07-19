language dcl 1.0

actor ApiService is system

shape UptimeRequest {
  // Represents the GET /uptime request, which is read-only and requires no input payload.
}

shape UptimeResponse {
  service: Text required
  started_at: DateTime required
  uptime_seconds: Number required
}

outcome UptimeSuccess is UptimeResponse
outcome UptimeRejected

policy AvailabilityTolerance {
  availability {
    dependency_tolerance allowed
  }
}

capability GetUptime {
  intent UptimeRequest from ApiService

  outcomes {
    UptimeSuccess
    UptimeRejected
  }

  // Rule to enforce read-only nature (Behavior 4)
  rule ReadOnlyConstraint: input is not mutating

  effects {}

  policies {
    AvailabilityTolerance governs capability
  }

  observe {
    capability duration as uptime_read_duration
  }

  lifecycle {
    begin Pending
    end Success
    end Rejected
    move Pending to Success on outcome UptimeSuccess
    move Pending to Rejected on outcome UptimeRejected
  }

  when {
    // Successful read operation
    otherwise then UptimeSuccess

    // Mutation attempt rejection (Behavior 4)
    ReadOnlyConstraint violated then UptimeRejected
  }
}