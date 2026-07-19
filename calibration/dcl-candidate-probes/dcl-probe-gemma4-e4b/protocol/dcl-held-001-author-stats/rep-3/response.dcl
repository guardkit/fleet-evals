language dcl 1.0

shape StatsResponse {
  service: Text required
  requests_served: Number required
  first_request_at: DateTime required
}

shape StatsRequest {}

policy ReadOnlyAccess {
  governance {
    audit required
  }
}

policy HighAvailability {
  availability {
    dependency_tolerance allowed
  }
}

capability GetStats {
  intent StatsRequest from system

  outcomes {
    StatsReported
    ServiceDegraded
  }

  effects {}

  events {}

  policies {
    ReadOnlyAccess governs capability
    HighAvailability governs capability
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
    policy HighAvailability degraded then ServiceDegraded
    otherwise then StatsReported
  }
}