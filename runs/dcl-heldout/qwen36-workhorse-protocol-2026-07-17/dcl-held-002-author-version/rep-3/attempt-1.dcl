language dcl 1.0

actor ApiTestService is system

shape VersionRequest {
  method: Text required
}

outcome VersionRetrieved
outcome MethodNotAllowed

policy VersionPolicy {
  availability {
    degradation forbidden
  }
  security {
    authentication forbidden
  }
}

capability GetVersion {
  intent VersionRequest from ApiTestService

  outcomes {
    VersionRetrieved
    MethodNotAllowed
  }

  rules {
    IsGetRequest: input.method is "GET"
  }

  policies {
    VersionPolicy governs capability
    VersionPolicy governs lifecycle
  }

  observe {
    capability duration as version_endpoint_duration
    outcome VersionRetrieved count as version_requests
  }

  when {
    IsGetRequest violated then MethodNotAllowed
    otherwise then VersionRetrieved
  }

  lifecycle {
    begin step Pending
    end step Completed
    move Pending to Completed on outcome VersionRetrieved
    move Pending to Completed on outcome MethodNotAllowed
  }
}