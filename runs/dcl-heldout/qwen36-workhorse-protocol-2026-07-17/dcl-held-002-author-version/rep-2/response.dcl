language dcl 1.0

actor Client is human

shape VersionRequest {
  requestId: Uuid required
}

shape VersionResponse {
  version: Text required
  commit: Text required
  service: Text required
}

effect ReadMetadata is invocation

policy VersionAvailability {
  availability {
    degradation allowed
  }
}

capability GetVersion {
  intent VersionRequest from Client

  outcomes {
    VersionRetrieved
  }

  effects {
    ReadMetadata
  }

  policies {
    VersionAvailability governs capability
    VersionAvailability governs lifecycle
  }

  observe {
    capability duration
    outcome VersionRetrieved count as version_requests
  }

  when {
    otherwise then VersionRetrieved
  }

  lifecycle {
    begin Started
    step Active
    end Done
    move Started to Active on outcome VersionRetrieved
    move Active to Done on outcome VersionRetrieved
  }
}