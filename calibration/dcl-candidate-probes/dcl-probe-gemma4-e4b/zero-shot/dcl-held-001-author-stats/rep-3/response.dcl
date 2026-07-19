language dcl 1.0

actor System is system

shape StatsResponse {
  service: Text required
  requests_served: Integer required
  first_request_at: Text required
}

capability GetStats {
  intent from System

  outcomes {
    StatsResponse
  }

  // Since this is a read-only endpoint, the lifecycle is minimal.
  lifecycle {
    begin Active
    step Active
    end Active
  }

  // Policy governing the read-only nature (GET only)
  policies {
    ReadAccess governs capability
  }

  // The capability itself represents the successful execution of the GET /stats request.
  when {
    otherwise then StatsResponse
  }
}

policy ReadAccess {
  // Ensures that only read operations are permitted on this capability
  read_only required
}