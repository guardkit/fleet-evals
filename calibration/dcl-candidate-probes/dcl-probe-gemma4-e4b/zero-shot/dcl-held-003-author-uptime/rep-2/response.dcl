language dcl 1.0

actor System is system

shape UptimeResponse {
  service: Text required
  started_at: Text required
  uptime_seconds: Decimal required
}

outcome UptimeAvailable

capability GetUptime {
  intent () from System

  outcomes {
    UptimeAvailable
  }

  rule UptimeValid: outcome.uptime_seconds >= 0

  effects {}

  events {}

  policies {}

  observe {
    capability duration
    outcome UptimeAvailable count as successful_uptime_reads
  }

  when {
    UptimeValid violated then {}
    otherwise then UptimeAvailable
  }

  lifecycle {
    begin Idle
    step Idle
    step Active waits for outcome UptimeAvailable
    end Active
    end Idle
    move Idle to Active on intent
    move Active to Idle on outcome UptimeAvailable
  }
}