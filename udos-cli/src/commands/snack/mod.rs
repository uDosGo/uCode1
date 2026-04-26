//! Snack CLI commands

use clap::{Arg, ArgMatches, Command};
use std::path::PathBuf;

pub mod list;
pub mod show;
pub mod run;
pub mod create;

/// Register snack commands
pub fn register() -> Command {
    Command::new("snack")
        .about("Manage executable snacks")
        .subcommand(list::register())
        .subcommand(show::register())
        .subcommand(run::register())
        .subcommand(create::register())
}

/// Handle snack commands
pub fn handle(matches: &ArgMatches) -> Result<(), Box<dyn std::error::Error>> {
    match matches.subcommand() {
        Some(("list", sub_matches)) => list::handle(sub_matches),
        Some(("show", sub_matches)) => show::handle(sub_matches),
        Some(("run", sub_matches)) => run::handle(sub_matches),
        Some(("create", sub_matches)) => create::handle(sub_matches),
        _ => Ok(()),
    }
}
