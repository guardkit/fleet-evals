language dcl 1.0

actor Client is machine

effect ReadProcessStats is in_memory

policy StatsReadonlyPolicy {
  reliability {
    retry {
      attempts 1
      backoff exponential
    }
    idempotency required
    timeout 5 seconds
  }
}

shape StatsRequest {
  method: Text required
  path: Text required
}

event StatsRetrievedEvent is {
  service: Text required
  requests_served: Integer required
  first_request_at: Text required
}

capability GetStats {
  intent StatsRequest from Client

  outcomes {
    StatsRetrieved
  }

  rule MethodGet: input.method is GET

  effects {
    ReadProcessStats
  }

  events {
    emits StatsRetrievedEvent
  }

  policies {
    StatsReadonlyPolicy governs capability
    StatsReadonlyPolicy governs effect ReadProcessStats
    StatsReadonlyPolicy governs lifecycle
  }

  observe {
    capability duration
    outcome StatsRetrieved count as stats_requests_served
    effect ReadProcessStats count failures as stats_read_failures
    lifecycle transitions
  }

  when {
    MethodGet violated then StatsRetrieved
    otherwise then StatsRetrieved
  }

  lifecycle {
    begin Pending
    step Pending
    step Active waits for event StatsRetrievedEvent
    end Served
    move Pending to Active on outcome StatsRetrieved
    move Active to Served on event StatsRetrievedEvent
  }
}