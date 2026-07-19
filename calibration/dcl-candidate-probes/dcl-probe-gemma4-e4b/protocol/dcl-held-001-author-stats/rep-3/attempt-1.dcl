language dcl 1.0

shape StatsResponse {
  service: Text required
  requests_served: Number required
  first_request_at: DateTime required
}

outcome StatsReported is StatsResponse
outcome ServiceDegraded

policy ReadOnlyAccess {
  governance {
    audit required
  }
}

policy HighAvailability {
  availability {
    dependency_tolerance required
    degradation allowed
  }
}

capability GetStats {
  intent from system

  outcomes {
    StatsReported
    ServiceDegraded
  }

  effects {}

  events {}

  policies {
    HighAvailability governs capability
    ReadOnlyAccess governs capability
  }

  observe {
    capability duration as stats_latency
  }

  lifecycle {
    begin Active
    end Completed
    step Active {
      kind active
      deadline 5 seconds causing outcome ServiceDegraded
    }
    move Active to Completed on outcome StatsReported
    move Active to Completed on outcome ServiceDegraded
  }

  when {
    otherwise then StatsReported
  }
}