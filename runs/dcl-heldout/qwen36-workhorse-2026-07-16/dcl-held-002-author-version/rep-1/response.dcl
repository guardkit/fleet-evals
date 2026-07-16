language dcl 1.0

actor Client is system

shape VersionRequestInput {}

policy VersionAccessPolicy {
  reliability {
    timeout 5 seconds
  }
}

effect FetchBuildMetadata is system

capability GetVersion {
  intent VersionRequestInput from Client

  outcomes {
    VersionRetrieved
    MethodNotAllowed
  }

  rule IsGetRequest: true

  effects {
    FetchBuildMetadata
  }

  policies {
    VersionAccessPolicy governs capability
    VersionAccessPolicy governs effect FetchBuildMetadata
    VersionAccessPolicy governs lifecycle
  }

  observe {
    capability duration
    outcome VersionRetrieved count as version_requests_served
    outcome MethodNotAllowed count as version_method_rejections
  }

  when {
    FetchBuildMetadata resolved then VersionRetrieved
    otherwise then MethodNotAllowed
  }

  lifecycle {
    begin Pending
    step Processing
    end Served
    end Rejected
    move Pending to Processing on outcome VersionRetrieved
    move Processing to Served on effect FetchBuildMetadata
    move Pending to Rejected on outcome MethodNotAllowed
  }
}