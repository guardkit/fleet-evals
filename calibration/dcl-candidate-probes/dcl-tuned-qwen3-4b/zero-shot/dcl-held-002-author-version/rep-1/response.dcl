language dcl 1.0

actor Requester is human

shape VersionInput {
  version: Text required
  commit: Text required
  service: Text required
}

event VersionRequested is {
  method: Text required
}

outcome VersionResponse is {
  version: Text required
  commit: Text required
  service: Text required
}

event MethodNotAllowed is {
  method: Text required
}

policy VersionEndpointReliability {
  reliability {
    timeout 5 seconds
  }
}

capability ApiVersionEndpoint {
  intent VersionInput from Requester

  outcomes {
    VersionResponse
  }

  rule MethodIsGet: input.method is "GET"

  effects {
    return VersionResponse
  }

  events {
    emits VersionRequested
  }

  policies {
    VersionEndpointReliability governs capability
  }

  observe {
    capability duration
    outcome VersionResponse count as version_requests_succeeded
  }

  when {
    MethodIsGet violated then MethodNotAllowed
    otherwise then VersionResponse
  }

  lifecycle {
    begin Pending
    step Pending
    end Success
    move Pending to Success on outcome VersionResponse
  }
}
