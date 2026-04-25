// src/mcp/tools/discover_repo.rs
use serde::{Deserialize, Serialize};
use std::process::Command;

#[derive(Debug, Serialize, Deserialize)]
pub struct DiscoverRepoInput {
    pub repo_url: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct DiscoverRepoOutput {
    pub success: bool,
    pub message: String,
    pub logs: String,
}

pub fn discover_repo(input: DiscoverRepoInput) -> Result<DiscoverRepoOutput, String> {
    let temp_dir = tempfile::tempdir()
        .map_err(|e| format!("Failed to create temp directory: {}", e))?;
    let repo_path = temp_dir.path().join("repo");

    let clone_output = Command::new("git")
        .args(&["clone", &input.repo_url, repo_path.to_str().unwrap()])
        .output()
        .map_err(|e| format!("Failed to clone repo: {}", e))?;

    if !clone_output.status.success() {
        return Err(format!(
            "Failed to clone repo: {}",
            String::from_utf8_lossy(&clone_output.stderr)
        ));
    }

    let setup_output = Command::new("bash")
        .args(&["-c", "if [ -f setup.sh ]; then ./setup.sh; fi"])
        .current_dir(&repo_path)
        .output()
        .map_err(|e| format!("Failed to run setup script: {}", e))?;

    let build_output = Command::new("bash")
        .args(&["-c", "if [ -f build.sh ]; then ./build.sh; elif [ -f Makefile ]; then make build; fi"])
        .current_dir(&repo_path)
        .output()
        .map_err(|e| format!("Failed to run build script: {}", e))?;

    let test_output = Command::new("bash")
        .args(&["-c", "if [ -f test.sh ]; then ./test.sh; elif [ -f Makefile ]; then make test; fi"])
        .current_dir(&repo_path)
        .output()
        .map_err(|e| format!("Failed to run test script: {}", e))?;

    let logs = format!(
        "Clone output:\\n{}\\n\\nSetup output:\\n{}\\n\\nBuild output:\\n{}\\n\\nTest output:\\n{}",
        String::from_utf8_lossy(&clone_output.stdout),
        String::from_utf8_lossy(&setup_output.stdout),
        String::from_utf8_lossy(&build_output.stdout),
        String::from_utf8_lossy(&test_output.stdout)
    );

    Ok(DiscoverRepoOutput {
        success: build_output.status.success() && test_output.status.success(),
        message: "Repo discovery completed".to_string(),
        logs,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_discover_repo_invalid_url() {
        let input = DiscoverRepoInput {
            repo_url: "invalid-url".to_string(),
        };
        let result = discover_repo(input);
        assert!(result.is_err());
    }
}