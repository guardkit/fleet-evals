language dcl 1.0

actor Client is system

effect ComputeStats is computation
effect SendStatsResponse is network

policy StatsReadonlyPolicy {
  reliability {
    idempotency required
    timeout 5 seconds
  }
}

shape StatsRequest {
  method: Text required
}

shape StatsResponse {
  service: Text required
  requests_served: Integer required
  first_request_at: Text required
}

event StatsRequestHandled is {
  service: Text required
  requests_served: Integer required
}

capability GetStats {
  intent StatsRequest from Client

  outcomes {
    StatsReturned
    MethodNotAllowed
  }

  rule GetOnly: input.method is "GET"

  effects {
    ComputeStats
    SendStatsResponse after ComputeStats
  }

  events {
    emits StatsRequestHandled
  }

  policies {
    StatsReadonlyPolicy governs capability
    StatsReadonlyPolicy governs effect SendStatsResponse
    StatsReadonlyPolicy governs lifecycle
  }

  observe {
    capability duration
    outcome StatsReturned count as stats_requests_served
    effect ComputeStats count as stats_computations
    lifecycle transitions
  }

  when {
    GetOnly violated then MethodNotAllowed
    otherwise then StatsReturned
  }

  lifecycle {
    begin Idle
    step Processing waits for event StatsRequestHandled
    end Served
    move Idle to Processing on outcome StatsReturned
    move Processing to Served on event StatsRequestHandled
    move Idle to Served on outcome MethodNotAllowed
  }
}