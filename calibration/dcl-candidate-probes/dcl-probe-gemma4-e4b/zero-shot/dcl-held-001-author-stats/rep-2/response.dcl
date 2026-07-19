language dcl 1.0

actor system is system

shape StatsReport {
  service: Text required
  requests_served: Integer required
  first_request_at: Text required
}

capability GetStats {
  intent void

  outcomes {
    StatsReport
  }

  policies {
    DataIntegrity governs capability
  }

  observe {
    capability duration
    outcome StatsReport count as stats_reports_served
  }

  lifecycle {
    begin Starting
    step Running
    end Running
    move Starting to Running on capability initialized
  }
}

policy DataIntegrity {
  consistency {
    read_only required
    state_persistence required
  }
}