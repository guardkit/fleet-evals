language dcl 1.0

actor Client is system

effect UpdateStatsCounter is persistence

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

shape StatsRequest {
  method: Text required
}

event StatsUpdated is {
  service: Text required
  requests_served: Integer required
  first_request_at: Text required
}

capability GetStats {
  intent StatsRequest from Client

  outcomes {
    StatsReturned
  }

  effects {
    UpdateStatsCounter
  }

  events {
    emits StatsUpdated
  }

  policies {
    StatsReliability governs capability
    StatsReliability governs effect UpdateStatsCounter
    StatsReliability governs lifecycle
  }

  observe {
    capability duration
    outcome StatsReturned count as stats_requests_served
    effect UpdateStatsCounter count as stats_counter_updates
    lifecycle transitions
  }

  when {
    UpdateStatsCounter resolved then StatsReturned
    otherwise then StatsReturned
  }

  lifecycle {
    begin Pending
    step Processing
    end Completed
    end Failed
    move Pending to Processing on outcome StatsReturned
    move Processing to Completed on event StatsUpdated
    move Pending to Failed on outcome StatsReturned
  }
}