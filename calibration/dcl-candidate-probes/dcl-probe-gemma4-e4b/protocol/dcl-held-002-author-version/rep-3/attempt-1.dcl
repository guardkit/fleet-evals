language dcl 1.0

shape VersionResponse {
  version: Text required
  commit: Text required
  service: Text required
}

shape Request {
  method: Text required
  path: Text required
}

actor Service is system

policy ReadAccessPolicy {
  security {
    authentication allow
    authorization allow
  }
}

policy DegradationPolicy {
  availability {
    dependency_tolerance allowed
  }
}

capability GetVersion {
  intent Request from Service

  outcomes {
    VersionSuccess is VersionResponse
    MethodRejected
  }

  effects {}

  events {}

  policies {
    ReadAccessPolicy governs capability
    DegradationPolicy governs capability
  }

  observe {
    capability duration as version_lookup_time
  }

  when {
    // If the method is GET and the path is /version, success.
    method is "GET" and path is "/version" then VersionSuccess
    // All other methods/paths are rejected as method not allowed.
    otherwise then MethodRejected
  }

  lifecycle {
    begin Pending
    end Completed
    step Pending {
      kind active
    }
    move Pending to Completed on outcome VersionSuccess
    move Pending to Completed on outcome MethodRejected
  }
}