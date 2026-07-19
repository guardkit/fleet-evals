language dcl 1.0

actor Client is system

shape VersionRequest {}
shape VersionResponse {
  version: Text required
  commit: Text required
  service: Text required
}

outcome Success
outcome Failure

capability GetVersion {
  intent VersionRequest from Client

  outcomes {
    Success
    Failure
  }

  policies {
    // Behavior 4: No authentication required
    security {
      authentication allow
    }
    // Pass-bar: NO degradation when DB is down (dependency_tolerance allowed)
    availability {
      dependency_tolerance allowed
    }
    // General operational reliability
    reliability {
      timeout 10 seconds
    }
  }

  observe {
    capability duration as version_read_time
  }

  lifecycle {
    begin Pending
    end Completed
    step Pending {
      kind active
      deadline 10 seconds causing outcome Failure
    }
    move Pending to Completed on outcome Success
    move Pending to Completed on outcome Failure
  }

  when {
    // Success is the default outcome if no policy or deadline violation occurs
    otherwise then Success
  }
}