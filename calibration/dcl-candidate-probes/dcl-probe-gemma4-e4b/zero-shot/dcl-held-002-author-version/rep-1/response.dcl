language dcl 1.0

actor ApiService is system

shape VersionResponse {
  version: Text required
  commit: Text required
  service: Text required
}

shape VersionRequest {}

outcome VersionSuccess

outcome MethodNotAllowed

capability GetVersion {
  intent VersionRequest from ApiService

  outcomes {
    VersionSuccess
    MethodNotAllowed
  }

  effects {}

  events {}

  policies {
    // Enforce read-only nature
    ReadWriteConstraint governs capability
    // Enforce no database dependency
    NoDatabaseDependency governs capability
    // Enforce public access (no auth required)
    PublicAccess governs capability
  }

  observe {
    capability duration
    outcome VersionSuccess count as successful_versions
    outcome MethodNotAllowed count as rejected_methods
  }

  when {
    // If the request is a GET, it succeeds with the version data
    is_get then VersionSuccess
    // If the request is not GET, it is rejected
    is_not_get then MethodNotAllowed
  }

  lifecycle {
    begin Initial
    end Complete
    move Initial to Complete on outcome VersionSuccess
    move Initial to Complete on outcome MethodNotAllowed
  }
}

// --- Policy Definitions ---

policy ReadWriteConstraint {
  // This policy ensures that only GET requests are allowed for this capability
  // (modeled via the 'when' clause in the capability itself, but declared here for completeness)
  enforce {
    method is GET
  }
}

policy NoDatabaseDependency {
  // This policy ensures the endpoint is non-blocking and independent of external state
  dependency_down_degradation required
}

policy PublicAccess {
  // This policy ensures no authentication is required
  authentication required none
}

// --- Utility Definitions (for compilation) ---

// Helper predicate to check HTTP method
predicate is_get {
  method is GET
}

predicate is_not_get {
  method is not GET
}