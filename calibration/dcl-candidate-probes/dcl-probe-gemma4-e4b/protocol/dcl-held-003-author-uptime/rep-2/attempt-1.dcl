language dcl 1.0

actor System is system

shape UptimeResponse {
  service: Text required
  started_at: DateTime required
  uptime_seconds: Number required
}

shape UptimeRequest {}

outcomes {
  UptimeAvailable is UptimeResponse
  UptimeUnavailable
}

policy HighAvailability {
  availability {
    dependency_tolerance allowed
  }
}

policy FastResponse {
  performance {
    latency 99.9% under 100ms
  }
}

capability GetUptime {
  intent UptimeRequest from System

  outcomes {
    UptimeAvailable
    UptimeUnavailable
  }

  rules {
    NonNegativeUptime: uptime_seconds >= 0
  }

  effects {}
  events {}

  policies {
    HighAvailability governs capability
    FastResponse governs capability
  }

  observe {
    capability duration as uptime_query_duration
  }

  lifecycle {
    begin Active
    end Active
    step Active {
      kind active
    }
    move Active to Success on outcome UptimeAvailable
    move Active to Failure on outcome UptimeUnavailable
  }

  when {
    NonNegativeUptime violated then UptimeUnavailable
    otherwise then UptimeAvailable
  }
}