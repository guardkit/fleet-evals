language dcl 1.0

actor Client is human

shape VersionRequest {
  method: Text required
}

effect ReadMetadata is persistence

event VersionRetrievedEvent is {
  version: Text required
  commit: Text required
  service: Text required
}

outcome VersionRetrieved
outcome MethodNotAllowed

policy ReadPolicy {
  reliability {
    timeout 5 seconds
  }
}

capability GetVersion {
  intent VersionRequest from Client

  outcomes {
    VersionRetrieved
    MethodNotAllowed
  }

  effects {
    ReadMetadata
  }

  events {
    emits VersionRetrievedEvent
  }

  policies {
    ReadPolicy governs capability
    ReadPolicy governs effect ReadMetadata
    ReadPolicy governs lifecycle
  }

  observe {
    capability duration
    outcome VersionRetrieved count as version_requests
    effect ReadMetadata count failures as read_failures
    lifecycle transitions
  }

  when {
    otherwise then VersionRetrieved
  }

  lifecycle {
    begin Pending
    step Ready
    end Retrieved
    move Pending to Ready on outcome MethodNotAllowed
    move Ready to Retrieved on outcome VersionRetrieved
  }
}