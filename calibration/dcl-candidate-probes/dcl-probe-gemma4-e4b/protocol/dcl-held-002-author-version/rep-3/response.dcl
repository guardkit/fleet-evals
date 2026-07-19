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

outcome VersionSuccess is VersionResponse
outcome MethodRejected

policy PublicAccess {
  security {
    authentication allowed
    authorization allowed
  }
}

policy NoDegradation {
  availability {
    dependency_tolerance allowed
  }
}

capability GetVersion {
  intent Request from Service

  outcomes {
    VersionSuccess
    MethodRejected
  }

  effects {}

  events {}

  policies {
    PublicAccess governs capability
    NoDegradation governs capability
  }

  observe {
    capability duration as version_lookup_time
  }

  when {
    method is "GET" and path is "/version" then VersionSuccess
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