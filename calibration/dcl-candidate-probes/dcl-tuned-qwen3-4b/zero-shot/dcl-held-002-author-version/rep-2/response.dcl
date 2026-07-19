language dcl 1.0

actor Requester is human

shape VersionRequest {
  method: Method required
}

event VersionResponse is {
  version: Text required
  commit: Text required
  service: Text required
}

event MethodNotAllowed is {
  method: Method required
}

outcome VersionReturned
outcome MethodNotAllowedResponse

policy VersionEndpointReliability {
  reliability {
    timeout 10 seconds
  }
}

capability ApiVersionEndpoint {
  intent VersionRequest from Requester

  outcomes {
    VersionReturned
    MethodNotAllowedResponse
  }

  rule MethodIsGet: input.method is "GET"

  effects {
    return VersionResponse
  }

  events {
    emits VersionResponse
    emits MethodNotAllowed
  }

  policies {
    VersionEndpointReliability governs capability
  }

  observe {
    capability duration
    outcome VersionReturned count as version_requests_succeeded
    event MethodNotAllowed count failures as method_not_allowed_failures
  }

  when {
    MethodIsGet violated then MethodNotAllowedResponse
    otherwise then VersionReturned
  }

  lifecycle {
    begin Pending
    step Pending
    step Completed
    end Completed
    move Pending to Completed on outcome VersionReturned
  }
}
