language dcl 1.0

actor SystemClient is system

shape VersionInfo {
  version: Text required
  commit: Text required
  service: Text required
}

outcome VersionRetrieved is VersionInfo

outcome MethodNotAllowed

outcome ServiceError

capability GetVersion {
  intent SystemClient

  outcomes {
    VersionRetrieved
    MethodNotAllowed
    ServiceError
  }

  // Since this is a GET request, the primary rule is that the method must be GET.
  // We model the successful path based on the GET request.
  rule IsGetRequest: input is GET

  // No effects are needed as it is read-only and non-persistent.
  effects {}

  // No events are emitted.
  events {}

  // No specific policies needed beyond general system constraints.
  policies {}

  observe {
    // Observe the successful retrieval of version info
    outcome VersionRetrieved count as successful_version_retrievals
    // Observe failures
    outcome MethodNotAllowed count as method_not_allowed_count
    outcome ServiceError count as service_errors
  }

  when {
    // If the request is not GET, it results in MethodNotAllowed
    IsGetRequest violated then MethodNotAllowed
    // If the service fails to retrieve the data (e.g., internal error), it results in ServiceError
    // (We assume this is handled internally if the rule passes, but we must define the failure path)
    // For simplicity, we assume if the rule passes and no error is explicitly thrown, it succeeds.
    otherwise then VersionRetrieved
  }

  lifecycle {
    begin Pending
    step Pending
    end Complete
    end Failed
    move Pending to Complete on outcome VersionRetrieved
    move Pending to Failed on outcome MethodNotAllowed
    move Pending to Failed on outcome ServiceError
  }
}