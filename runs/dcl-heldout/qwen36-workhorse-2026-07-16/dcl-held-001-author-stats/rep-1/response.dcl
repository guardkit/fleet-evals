language dcl 1.0

actor Client is system

effect ComputeProcessStats is computation

policy StatsReliability {
  reliability {
    retry {
      attempts 1
      backoff exponential
    }
    idempotency required
    timeout 5 seconds
  }
}

shape StatsRequestInput {
  method: Text required
}

event StatsComputed is {
  service: Text required
  requests_served: Integer required
  first_request_at: DateTime required
}

capability GetStats {
  intent StatsRequestInput from Client

  outcomes {
    StatsReturned
    MethodNotAllowed
  }

  rule IsGet: input.method is "GET"

  effects {
    ComputeProcessStats
  }

  events {
    emits StatsComputed
  }

  policies {
    StatsReliability governs capability
    StatsReliability governs effect ComputeProcessStats
  }

  observe {
    capability duration
    outcome StatsReturned count as stats_requests_served
    effect ComputeProcessStats count as stats_computations
  }

  when {
    IsGet violated then MethodNotAllowed
    otherwise then StatsReturned
  }

  lifecycle {
    begin Pending
    step Processing
    end Served
    end Rejected
    move Pending to Processing on outcome StatsReturned
    move Pending to Rejected on outcome MethodNotAllowed
    move Processing to Served on event StatsComputed
  }
}