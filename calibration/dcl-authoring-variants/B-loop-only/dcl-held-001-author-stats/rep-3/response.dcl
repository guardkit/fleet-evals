language dcl 1.0

actor Client is system

shape StatsRequest {
  method: Text required
}

effect ReadProcessState is persistence

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

event StatsRetrievedEvent is {
  service: Text required
  requests_served: Integer required
  first_request_at: Text required
}

capability GetStats {
  intent StatsRequest from Client

  outcomes {
    StatsRetrieved
    MethodNotAllowed
  }

  rule AllowedMethod: input.method is GET

  effects {
    ReadProcessState
  }

  events {
    emits StatsRetrievedEvent
  }

  policies {
    StatsReliability governs capability
    StatsReliability governs effect ReadProcessState
    StatsReliability governs lifecycle
  }

  observe {
    capability duration
    outcome StatsRetrieved count as stats_requests
    lifecycle transitions
  }

  when {
    AllowedMethod violated then MethodNotAllowed
    otherwise then StatsRetrieved
  }

  lifecycle {
    begin Pending
    step Processing
    end Completed
    end Rejected
    move Pending to Processing on outcome StatsRetrieved
    move Pending to Rejected on outcome MethodNotAllowed
  }
}