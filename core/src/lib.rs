//! uCode1 Core Library
//!
//! Core functionality for the uCode1 platform

pub mod snack;
pub mod relic;
pub mod binder;
pub mod usxd;

/// Get core system version
pub fn version() -> &'static str {
    env!("CARGO_PKG_VERSION")
}
