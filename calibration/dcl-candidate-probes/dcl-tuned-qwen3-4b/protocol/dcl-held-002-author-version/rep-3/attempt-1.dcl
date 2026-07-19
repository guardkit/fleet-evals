language dcl 1.0

actor Requester is human

shape VersionResponse {
  version: Text required
  commit: Text required
  service: Text required
}

event VersionRequested is {
  method: Text required
}

effect ReturnVersion is persistence

policy VersionReliability {
  reliability {
    timeout 10 seconds
    idempotency required
  }
}

capability GetVersion {
  intent VersionResponse from Requester

  outcomes {
    VersionReturned
  }

  rules {
    ValidResponse: version is not null and commit is not null and service is not null
  }

  effects {
    ReturnVersion
  }

  events {
    emits VersionRequested
  }

  policies {
    VersionReliability governs capability
  }

  observe {
    capability duration as get_version_duration
  }

  when {
    ValidResponse violated then VersionReturned
    otherwise then VersionReturned
  }

  lifecycle {
    begin step Started
    end step Completed
    step Started {
      kind active
    }
    move Started to Completed on outcome VersionReturned
  }
}
