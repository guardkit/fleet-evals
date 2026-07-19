language dcl 1.0

actor Service is system

shape VersionMetadata {
  version: Text required
  commit: Text required
  service: Text required
}

shape GetVersionRequest {
  // Represents the context of a GET request, no body payload required
}

outcome VersionRetrieved is VersionMetadata

outcome MethodNotAllowed

policy ReadOnlyPolicy {
  security {
    authentication allow
  }
  availability {
    dependency_tolerance required
  }
}

capability GetVersion {
  intent GetVersionRequest from Service

  outcomes {
    VersionRetrieved
    MethodNotAllowed
  }

  effects {}

  events {}

  policies {
    ReadOnlyPolicy governs capability
  }

  observe {
    capability duration as version_retrieval_time
  }

  lifecycle {
    begin Pending
    end Completed
    step Pending {
      kind active
      deadline 500ms causing outcome MethodNotAllowed
    }
    move Pending to Completed on outcome VersionRetrieved
  }

  when {
    // If the request is a GET, it succeeds and returns metadata
    // We model the success path as the default/otherwise case, assuming the intent
    // is only invoked for valid requests.
    otherwise then VersionRetrieved
    // If the request is not a GET (e.g., POST, PUT), it fails immediately
    // This models the "method-not-allowed" requirement.
    MethodNotAllowed violated then MethodNotAllowed
  }
}