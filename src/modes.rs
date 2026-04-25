// Mode handling for uCode1
// Controls feature activation based on CLI flags

#[derive(Debug, Clone)]
pub struct AppMode {
    pub user_mode: bool,
    pub privacy_mode: bool,
    pub status_mode: bool,
    pub dev_mode: bool,
    pub debug_mode: bool,
    pub roadmap_mode: bool,
}

impl AppMode {
    pub fn new() -> Self {
        AppMode {
            user_mode: true, // default
            privacy_mode: false,
            status_mode: false,
            dev_mode: false,
            debug_mode: false,
            roadmap_mode: false,
        }
    }

    /// Parse mode flags from CLI arguments
    pub fn from_flags(
        user: bool,
        privacy: bool,
        status: bool,
        dev: bool,
        debug: bool,
        roadmap: bool,
    ) -> Self {
        // Privacy mode overrides other modes for security
        let privacy_mode = privacy;
        
        AppMode {
            user_mode: user && !privacy_mode,
            privacy_mode,
            status_mode: status && !privacy_mode,
            dev_mode: dev && !privacy_mode,
            debug_mode: debug && !privacy_mode,
            roadmap_mode: roadmap && !privacy_mode,
        }
    }

    /// Should MCP server be enabled?
    pub fn mcp_enabled(&self) -> bool {
        self.status_mode || self.dev_mode
    }

    /// Should telemetry be enabled?
    pub fn telemetry_enabled(&self) -> bool {
        self.user_mode && !self.privacy_mode
    }

    /// Should feed processing be enabled?
    pub fn feeds_enabled(&self) -> bool {
        self.user_mode && !self.privacy_mode
    }

    /// Should debug logging be enabled?
    pub fn debug_logging(&self) -> bool {
        self.debug_mode || self.dev_mode
    }

    /// Is this a development/debug mode?
    pub fn is_dev(&self) -> bool {
        self.dev_mode
    }

    /// Get mode description
    pub fn description(&self) -> String {
        if self.privacy_mode {
            "privacy".to_string()
        } else if self.dev_mode {
            "dev".to_string()
        } else if self.status_mode {
            "status".to_string()
        } else if self.roadmap_mode {
            "roadmap".to_string()
        } else if self.debug_mode {
            "debug".to_string()
        } else {
            "user".to_string()
        }
    }
}

impl Default for AppMode {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_default_mode() {
        let mode = AppMode::new();
        assert!(mode.user_mode);
        assert!(!mode.privacy_mode);
        assert!(!mode.mcp_enabled());
    }

    #[test]
    fn test_privacy_mode_overrides() {
        let mode = AppMode::from_flags(false, true, false, false, false, false);
        assert!(mode.privacy_mode);
        assert!(!mode.user_mode);
        assert!(!mode.mcp_enabled());
    }

    #[test]
    fn test_status_mode() {
        let mode = AppMode::from_flags(false, false, true, false, false, false);
        assert!(mode.status_mode);
        assert!(mode.mcp_enabled());
    }

    #[test]
    fn test_dev_mode() {
        let mode = AppMode::from_flags(false, false, false, true, false, false);
        assert!(mode.dev_mode);
        assert!(mode.mcp_enabled());
        assert!(mode.debug_logging());
    }
}