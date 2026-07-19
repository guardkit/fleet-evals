language dcl 1.0

actor Client is client
actor Service is system

shape UptimeRequest {
  // Minimal request context for GET /uptime
}

shape UptimeResponse {
  service: Text required
  started_at: Text required
  uptime_seconds: Decimal required
}

outcome UptimeRetrieved

capability GetUptime {
  intent UptimeRequest from Client

  outcomes {
    UptimeRetrieved
  }

  // The capability is inherently read-only, enforced by the nature of the operation
  // and the lack of state modification effects.
  when {
    // If any attempt to mutate the state were detected (e.g., through an effect),
    // it would be rejected. Since we have no effects, the operation is read-only.
    otherwise then UptimeRetrieved
  }

  // No external effects are involved (read-only, internal process state)
  effects {}

  // No events are emitted for this synchronous read operation
  events {}

  // No specific policies govern this simple read operation
  policies {}

  observe {
    // Observe the successful retrieval of the response shape
    outcome UptimeRetrieved count as successful_reads
  }

  lifecycle {
    begin Pending
    step Pending
    step Completed
    end Completed
    move Pending to Completed on outcome UptimeRetrieved
  }
}