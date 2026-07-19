language dcl 1.0

actor Requester is human

shape VersionInput {
  version: Text required
  commit: Text required
  service: Text required
}

event VersionResponseSent is {
  version: Text required
  commit: Text required
  service: Text required
}

outcome VersionResponse is {
  version: Text required
  commit: Text required
  service: Text required
}

policy VersionEndpointReliability {
  reliability {
    timeout 30 seconds
  }
}

capability ApiVersionEndpoint {
  intent VersionInput from Requester

  outcomes {
    VersionResponse
  }

  rule RequestMethodIsGet: input.method is "GET"

  effects {
    // No effects — this is a read-only endpoint
  }

  events {
    emits VersionResponseSent
  }

  policies {
    VersionEndpointReliability governs capability
  }

  observe {
    capability duration
    outcome VersionResponse count as version_responses
    event VersionResponseSent count failures as version_response_sent_failures
  }

  when {
    RequestMethodIsGet violated then VersionResponse
    otherwise then VersionResponse
  }

  lifecycle {
    begin Pending
    step Pending
    end Ready
    move Pending to Ready on outcome VersionResponse
  }
}
