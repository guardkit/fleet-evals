language dcl 1.0

actor System is system

shape StatsRequest {}
shape StatsResponse {
  service: Text required
  requests_served: Integer required
  first_request_at: Text required
}

outcome StatsAvailable

policy ReadOnly {
  // Enforces that the capability is purely observational and non-mutating.
}

capability GetStats {
  intent StatsRequest from System

  outcomes {
    StatsAvailable
  }

  // The capability succeeds when the service successfully calculates and returns the stats.
  rule StatsCalculated: System can provide StatsResponse

  // Effects are empty as this is a read-only endpoint.
  effects {}

  // No events are emitted as this is a passive read operation.
  events {}

  policies {
    ReadOnly governs capability
  }

  // Lifecycle is simple, representing the continuous availability of the endpoint.
  lifecycle {
    begin Running
    end Running
  }

  // When the service is operational and can calculate the statistics, the outcome is achieved.
  when {
    StatsCalculated then StatsAvailable
  }
}