language dcl 1.0

actor Client is system

effect ReadStats is persistence

policy StatsReliability {
  reliability {
    retry {
      attempts 3
      backoff exponential
    }
    idempotency required
    timeout 30 seconds
  }
}

shape StatsRequest {
  method: Text required
}

event StatsRetrieved is {
  service: Text required
  requests_served: Integer required
  first_request_at: Text required
}

capability GetStats {
  intent StatsRequest from Client

  outcomes {
    StatsReturned
    MethodNotAllowed
  }

  rule AllowedMethod: input.method is GET

  effects {
    ReadStats
  }

  events {
    emits StatsRetrieved
  }

  policies {
    StatsReliability governs capability
  }

  observe {
    capability duration
    outcome StatsReturned count as stats_requests_served
    effect ReadStats count failures as counter_errors
    lifecycle transitions
  }

  when {
    AllowedMethod violated then MethodNotAllowed
    otherwise then StatsReturned
  }

  lifecycle {
    begin Idle
    step Active
    end Completed
    move Idle to Active on outcome StatsReturned
    move Active to Completed on event StatsRetrieved
  }
}