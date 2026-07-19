language dcl 1.0

actor Requester is system

shape VersionResponse {
  version: Text required
  commit: Text required
  service: Text required
}

// Outcomes
outcome Success is {
  response: VersionResponse
}
outcome Failure

// Policies
policy SecurityPolicy {
  security {
    authentication allow
  }
}

policy AvailabilityPolicy {
  availability {
    dependency_tolerance allowed
  }
}

policy ReliabilityPolicy {
  reliability {
    timeout 5 seconds
  }
}

// Capability
capability GetVersion {
  // Intent: GET /version (no input body required)
  intent EmptyRequest from Requester

  outcomes {
    Success
    Failure
  }

  policies {
    SecurityPolicy governs capability
    AvailabilityPolicy governs capability
    ReliabilityPolicy governs capability
  }

  observe {
    capability duration as version_read_time
  }

  lifecycle {
    begin Pending
    end Completed
    step Pending {
      kind active
      // Failure occurs if the operation exceeds the reliability timeout
      deadline 5 seconds causing outcome Failure
    }
    move Pending to Completed on outcome Success
    move Pending to Completed on outcome Failure
  }

  when {
    // Success is the default outcome if no failure/timeout occurs
    otherwise then Success
  }
}