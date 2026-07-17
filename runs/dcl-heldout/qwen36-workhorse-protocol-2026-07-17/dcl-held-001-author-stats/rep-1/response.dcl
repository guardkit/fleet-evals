language dcl 1.0

actor Client is system

shape StatsRequest {
  method: Text required
}

shape StatsResponse {
  service: Text required
  requestsServed: Number required
  firstRequestAt: DateTime required
}

event StatsServedEvent is {
  service: Text required
  requestsServed: Number required
}

effect ServeStats is invocation

policy StatsAvailability {
  availability {
    degradation forbidden
  }
}

capability GetStats {
  intent StatsRequest from Client

  outcomes {
    StatsServed
  }

  effects {
    ServeStats
  }

  events {
    emits StatsServedEvent
  }

  policies {
    StatsAvailability governs capability
    StatsAvailability governs lifecycle
  }

  observe {
    capability duration
  }

  when {
    otherwise then StatsServed
  }

  lifecycle {
    begin Pending
    end Served
    move Pending to Served on outcome StatsServed
  }
}