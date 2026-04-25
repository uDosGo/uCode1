// src/mcp/tools/spark_launch.rs
use serde::{Deserialize, Serialize};
use std::process::Command;

#[derive(Debug, Serialize, Deserialize)]
pub struct SparkLaunchInput {
    pub prompt: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SparkLaunchOutput {
    pub preview_url: String,
}

pub fn spark_launch(input: SparkLaunchInput) -> Result<SparkLaunchOutput, String> {
    let github_token = std::env::var("GITHUB_TOKEN")
        .map_err(|_| "GITHUB_TOKEN environment variable not set".to_string())?;

    let client = reqwest::blocking::Client::new();
    let response = client
        .post("https://spark.githubnext.com/api/generate")
        .header("Authorization", format!("Bearer {}", github_token))
        .json(&serde_json::json!({
            "prompt": input.prompt,
        }))
        .send()
        .map_err(|e| format!("Failed to call Spark API: {}", e))?;

    if !response.status().is_success() {
        return Err(format!(
            "Spark API returned error: {}",
            response.status()
        ));
    }

    let response_body: serde_json::Value = response
        .json()
        .map_err(|e| format!("Failed to parse Spark API response: {}", e))?;

    let preview_url = response_body["preview_url"]
        .as_str()
        .ok_or("Preview URL not found in Spark API response")?
        .to_string();

    Ok(SparkLaunchOutput { preview_url })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_spark_launch_missing_token() {
        std::env::remove_var("GITHUB_TOKEN");
        let input = SparkLaunchInput {
            prompt: "Test prompt".to_string(),
        };
        let result = spark_launch(input);
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("GITHUB_TOKEN"));
    }
}