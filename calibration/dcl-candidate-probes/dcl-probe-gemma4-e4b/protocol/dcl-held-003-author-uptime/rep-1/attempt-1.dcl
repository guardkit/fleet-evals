language dcl 1.0

shape UptimeRequest {
  // Since GET /uptime is read-only, the input shape is minimal, perhaps just context.
  // We assume the request context implies read-only intent.
}

shape UptimeResponse {
  service: Text required
  started_at: DateTime required
  uptime_seconds: Number required
}

// We use 'system' as the actor representing the API service itself or the caller context.
actor System is system

// No effects are needed as this is a read-only, self-contained query.

// Outcomes
outcome UptimeSuccess
outcome UptimeRejected

// Policy for robustness (ensuring availability, though trivial here)
policy HighAvailability {
  availability {
    dependency_tolerance allowed
  }
}

capability GetUptime {
  intent UptimeRequest from System

  outcomes {
    UptimeSuccess
    UptimeRejected
  }

  // Rule 1: Uptime must be non-negative.
  rule NonNegativeUptime: uptime_seconds >= 0

  // Policy application: Ensure the capability is robust against external failures (like DB down).
  policies {
    HighAvailability governs capability
  }

  // Lifecycle: Simple synchronous request/response cycle.
  lifecycle {
    begin Pending
    end Completed
    step Pending {
      kind active
      // Assume immediate processing for a simple GET request
    }
    move Pending to Completed on outcome UptimeSuccess
    move Pending to Completed on outcome UptimeRejected
  }

  // Causation logic:
  when {
    // If the request is valid and read-only, it succeeds.
    // We model the successful path based on the NonNegativeUptime rule passing.
    NonNegativeUptime violated then UptimeRejected // If the output violates the rule, it's rejected.
    // We assume any other valid request path leads to success.
    otherwise then UptimeSuccess
  }
}