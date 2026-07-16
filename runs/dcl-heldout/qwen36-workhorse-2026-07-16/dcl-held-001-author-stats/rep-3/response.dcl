language dcl 1.0

actor Client is system

effect UpdateCounter is persistence

policy StatsReliability {
  reliability {
    retry {
      attempts 1
      backoff linear
    }
    idempotency not_required
    timeout 5 seconds
  }
}

shape StatsRequest {}

event StatsRetrieved is {
  service: Text required
  requests_served: Integer required
  first_request_at: Text required
}

capability GetStats {
  intent StatsRequest from Client

  outcomes {
    StatsRetrieved
    MethodRejected
  }

  rule GetAllowed: true

  effects {
    UpdateCounter
  }

  events {
    emits StatsRetrieved
  }

  policies {
    StatsReliability governs capability
    StatsReliability governs effect UpdateCounter
    StatsReliability governs lifecycle
  }

  observe {
    capability duration
    outcome StatsRetrieved count as stats_requests_served
    effect UpdateCounter count as counter_increments
    lifecycle transitions
  }

  when {
    GetAllowed violated then MethodRejected
    UpdateCounter unresolved then StatsRetrieved
    otherwise then StatsRetrieved
  }

  lifecycle {
    begin Pending
    step Processing
    end Served
    move Pending to Processing on outcome StatsRetrieved
    move Pending to Served on outcome StatsRetrieved
    move Pending to Served on outcome MethodRejected
  }
}