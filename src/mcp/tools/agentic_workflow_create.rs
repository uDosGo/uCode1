// src/mcp/tools/agentic_workflow_create.rs
use serde::{Deserialize, Serialize};
use std::fs;
use std::path::Path;

#[derive(Debug, Serialize, Deserialize)]
pub struct AgenticWorkflowCreateInput {
    pub repo: String,
    pub workflow_name: String,
    pub description: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct AgenticWorkflowCreateOutput {
    pub success: bool,
    pub message: String,
}

pub fn agentic_workflow_create(input: AgenticWorkflowCreateInput) -> Result<AgenticWorkflowCreateOutput, String> {
    let github_token = std::env::var("GITHUB_TOKEN")
        .map_err(|_| "GITHUB_TOKEN environment variable not set".to_string())?;

    let workflow_content = format!(
        "name: {}\
\
\
on:\\n  workflow_dispatch:\\n\
\
jobs:\\n  agentic_workflow:\\n    runs-on: ubuntu-latest\\n    steps:\\n      - name: Execute Agentic Workflow\\n        uses: githubnext/agentic-workflows@v1\\n        with:\\n          description: '{}'\\n        env:\\n          GITHUB_TOKEN: ${{{{ secrets.GITHUB_TOKEN }}}}",
        input.workflow_name, input.description
    );

    let client = reqwest::blocking::Client::new();
    let response = client
        .put(&format!(
            "https://api.github.com/repos/{}/contents/.github/workflows/{}.md",
            input.repo, input.workflow_name
        ))
        .header("Authorization", format!("Bearer {}", github_token))
        .header("Accept", "application/vnd.github.v3+json")
        .json(&serde_json::json!({
            "message": "Add agentic workflow",
            "content": base64::encode(workflow_content),
        }))
        .send()
        .map_err(|e| format!("Failed to create workflow: {}", e))?;

    if !response.status().is_success() {
        return Err(format!(
            "GitHub API returned error: {}",
            response.status()
        ));
    }

    Ok(AgenticWorkflowCreateOutput {
        success: true,
        message: "Workflow created successfully".to_string(),
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_agentic_workflow_create_missing_token() {
        std::env::remove_var("GITHUB_TOKEN");
        let input = AgenticWorkflowCreateInput {
            repo: "test/repo".to_string(),
            workflow_name: "test".to_string(),
            description: "Test workflow".to_string(),
        };
        let result = agentic_workflow_create(input);
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("GITHUB_TOKEN"));
    }
}