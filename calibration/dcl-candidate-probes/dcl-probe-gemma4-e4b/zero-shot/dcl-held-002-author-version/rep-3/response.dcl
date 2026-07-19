language dcl 1.0

actor System is system

shape VersionRequest {
  method: HttpMethod required
  path: Text required
}

shape VersionResponse {
  version: Text required
  commit: Text required
  service: Text required
}

outcome VersionRetrieved

policy ReadOnlyPolicy {
  read_only {
    access_type read
  }
  dependency {
    database_access forbidden
    external_service_calls forbidden
  }
}

capability GetVersion {
  intent VersionRequest from System

  outcomes {
    VersionRetrieved
  }

  rule VersionData: outcome.VersionRetrieved requires VersionResponse

  effects {}

  events {}

  policies {
    ReadOnlyPolicy governs capability
  }

  observe {
    capability duration
    outcome VersionRetrieved count as successful_reads
  }

  when {
    // Successful read transition
    VersionRequest.method is GET and VersionRequest.path is "/version" then VersionRetrieved
    // Constraint enforcement (implicitly handled by policy/compiler, but good to model the rejection)
    VersionRequest.method is not GET then MethodNotAllowed
  }

  lifecycle {
    begin Pending
    step Pending
    end Success
    end Failure
    move Pending to Success on outcome VersionRetrieved
    move Pending to Failure on outcome MethodNotAllowed
  }
}