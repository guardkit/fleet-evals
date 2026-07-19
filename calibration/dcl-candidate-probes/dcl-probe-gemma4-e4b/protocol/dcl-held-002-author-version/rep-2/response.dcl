language dcl 1.0

actor Service is system

shape VersionMetadata {
  version: Text required
  commit: Text required
  service: Text required
}

shape RequestContext {
  method: Text required
}

outcome VersionRetrieved is VersionMetadata
outcome MethodNotAllowed

policy ReadOnlyPolicy {
  security {
    authentication allowed
  }
  availability {
    dependency_tolerance allowed
  }
}

capability GetVersion {
  intent RequestContext from Service

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

  rule IsGet: context.method is "GET"

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
    IsGet violated then MethodNotAllowed
    otherwise then VersionRetrieved
  }
}