// src/mcp/tools/flat_data_schedule.rs
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct FlatDataScheduleInput {
    pub repo: String,
    pub url: String,
    pub schedule: String,
    pub destination_path: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct FlatDataScheduleOutput {
    pub success: bool,
    pub message: String,
}

pub fn flat_data_schedule(input: FlatDataScheduleInput) -> Result<FlatDataScheduleOutput, String> {
    let github_token = std::env::var("GITHUB_TOKEN")
        .map_err(|_| "GITHUB_TOKEN environment variable not set".to_string())?;

    let workflow_content = format!(
        "name: Flat Data Schedule\\n\
on:\\n  schedule:\\n    - cron: '{}'\\n  workflow_dispatch:\\n\
jobs:\\n  fetch_data:\\n    runs-on: ubuntu-latest\\n    steps:\\n      - name: Checkout\\n        uses: actions/checkout@v4\\n      - name: Fetch Data\\n        uses: githubocto/flat@v3\\n        with:\\n          http_url: '{}'\\n          downloaded_filename: data.json\\n      - name: Commit Data\\n        run: |\\n          mkdir -p {}\\\\n          mv data.json {}\\\\n          git config --global user.name 'github-actions'\\n          git config --global user.email 'github-actions@github.com'\\n          git add .\\n          git commit -m 'Update data from {}'\\n          git push\\n        env:\\n          GITHUB_TOKEN: ${{{{ secrets.GITHUB_TOKEN }}}}",
        input.schedule, input.url, input.destination_path, input.destination_path, input.url
    );

    let client = reqwest::blocking::Client::new();
    let response = client
        .put(&format!(
            "https://api.github.com/repos/{}/contents/.github/workflows/flat-data.yml",
            input.repo
        ))
        .header("Authorization", format!("Bearer {}", github_token))
        .header("Accept", "application/vnd.github.v3+json")
        .json(&serde_json::json!({
            "message": "Add flat data schedule",
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

    Ok(FlatDataScheduleOutput {
        success: true,
        message: "Flat data schedule created successfully".to_string(),
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_flat_data_schedule_missing_token() {
        std::env::remove_var("GITHUB_TOKEN");
        let input = FlatDataScheduleInput {
            repo: "test/repo".to_string(),
            url: "https://example.com/data.json".to_string(),
            schedule: "0 0 * * *".to_string(),
            destination_path: "data/".to_string(),
        };
        let result = flat_data_schedule(input);
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("GITHUB_TOKEN"));
    }
}