// src/tools/mod.rs
// Re-export MCP tools for use by the HTTP server

pub mod spark_launch {
    pub use crate::mcp::tools::spark_launch::*;
}

pub mod agentic_workflow_create {
    pub use crate::mcp::tools::agentic_workflow_create::*;
}

pub mod flat_data_schedule {
    pub use crate::mcp::tools::flat_data_schedule::*;
}

pub mod copernicus_index {
    pub use crate::mcp::tools::copernicus_index::*;
}

pub mod discover_repo {
    pub use crate::mcp::tools::discover_repo::*;
}

pub mod plugin_list {
    pub use crate::mcp::tools::plugin_list::*;
}

pub mod system_status {
    pub use crate::mcp::tools::system_status::*;
}
