language dcl 1.0

// --- Actors ---
actor System is system

// --- Shapes ---
// Represents the input context for the GET request (read-only, no data payload)
shape RequestContext {}

// Represents the data returned by the successful uptime query
shape UptimeResponse {
  service: Text required
  started_at: DateTime required
  uptime_seconds: Number required
}

// --- Outcomes ---
// Success outcome, carrying the response data
outcome UptimeSuccess is UptimeResponse

// Failure outcome (e.g., unsupported operation, internal error)
outcome UptimeRejected

// --- Policies ---
// Policy ensuring the service remains available even if dependencies fail (DB down)
policy HighAvailability {
  availability {
    dependency_tolerance allowed
  }
}

// Policy ensuring the operation is read-only (cannot be mutated)
policy ReadOnly {
  governance {
    audit required
  }
}

// --- Capability ---
capability GetUptime {
  // Intent: The capability is triggered by a request context from the System actor.
  intent RequestContext from System

  outcomes {
    UptimeSuccess
    UptimeRejected
  }

  // Rules: Ensure the returned data adheres to constraints.
  // Rule 1: Uptime must be non-negative.
  rule NonNegativeUptime: uptime_seconds >= 0

  // Policies: Apply robustness and operational constraints.
  policies {
    HighAvailability governs capability
    ReadOnly governs capability
  }

  // Effects: This capability is read-only and self-contained, requiring no external effects.
  effects {}

  // Lifecycle: Simple synchronous request/response cycle.
  lifecycle {
    begin Pending
    end Completed
    step Pending {
      kind active
      // The operation is synchronous and immediate
    }
    move Pending to Completed on outcome UptimeSuccess
    move Pending to Completed on outcome UptimeRejected
  }

  // Causation logic:
  when {
    // If the output data violates the non-negative uptime rule, the request is rejected.
    NonNegativeUptime violated then UptimeRejected

    // If the request is valid and non-violating, it succeeds.
    otherwise then UptimeSuccess
  }
}