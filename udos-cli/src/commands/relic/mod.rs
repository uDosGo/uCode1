//! Relic CLI commands

use clap::{Arg, ArgMatches, Command};

pub mod create;
pub mod unpack;
pub mod list;
pub mod run;

/// Register relic commands
pub fn register() -> Command {
    Command::new("relic")
        .about("Manage snack relics (compressed snacks)")
        .subcommand(create::register())
        .subcommand(unpack::register())
        .subcommand(list::register())
        .subcommand(run::register())
}

/// Handle relic commands
pub fn handle(matches: &ArgMatches) -> Result<(), Box<dyn std::error::Error>> {
    match matches.subcommand() {
        Some(("create", sub_matches)) => create::handle(sub_matches),
        Some(("unpack", sub_matches)) => unpack::handle(sub_matches),
        Some(("list", sub_matches)) => list::handle(sub_matches),
        Some(("run", sub_matches)) => run::handle(sub_matches),
        _ => Ok(()),
    }
}
