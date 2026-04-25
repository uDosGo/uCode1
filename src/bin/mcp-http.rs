// uCode1/src/bin/mcp-http.rs
// HTTP wrapper for MCP tools using axum

use axum::{
    extract::Path,
    http::StatusCode,
    response::Json,
    routing::post,
    Router,
};
use serde_json::{json, Value};
use std::net::SocketAddr;

// Import your existing MCP tools directly
use ucode1_mcp::tools::spark_launch::{spark_launch, SparkLaunchInput};
use ucode1_mcp::tools::agentic_workflow_create::{agentic_workflow_create, AgenticWorkflowCreateInput};
use ucode1_mcp::tools::flat_data_schedule::{flat_data_schedule, FlatDataScheduleInput};
use ucode1_mcp::tools::copernicus_index::{copernicus_index, CopernicusIndexInput};
use ucode1_mcp::tools::discover_repo::{discover_repo, DiscoverRepoInput};
use ucode1_mcp::tools::system_status::system_status;
use ucode1_mcp::tools::plugin_list::plugin_list;

async fn handle_tool(Path(tool_name): Path<String>, Json(payload): Json<Value>) -> Result<Json<Value>, StatusCode> {
    let result: serde_json::Value = match tool_name.as_str() {
        "spark_launch" => {
            let prompt = payload["prompt"].as_str().ok_or(StatusCode::BAD_REQUEST)?;
            let input = SparkLaunchInput {
                prompt: prompt.to_string(),
            };
            let output = spark_launch(input).map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
            serde_json::to_value(output).unwrap()
        }
        "agentic_workflow_create" => {
            let desc = payload["description"].as_str().ok_or(StatusCode::BAD_REQUEST)?;
            let repo = payload["repo"].as_str().ok_or(StatusCode::BAD_REQUEST)?;
            let input = AgenticWorkflowCreateInput {
                repo: repo.to_string(),
                workflow_name: "workflow".to_string(), // Default name
                description: desc.to_string(),
            };
            let output = agentic_workflow_create(input).map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
            serde_json::to_value(output).unwrap()
        }
        "flat_data_schedule" => {
            let source = payload["source"].as_str().ok_or(StatusCode::BAD_REQUEST)?;
            let schedule = payload["schedule"].as_str().ok_or(StatusCode::BAD_REQUEST)?;
            let repo = payload["repo"].as_str().ok_or(StatusCode::BAD_REQUEST)?;
            let input = FlatDataScheduleInput {
                repo: repo.to_string(),
                url: source.to_string(),
                schedule: schedule.to_string(),
                destination_path: "data/".to_string(),
            };
            let output = flat_data_schedule(input).map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
            serde_json::to_value(output).unwrap()
        }
        "copernicus_index" => {
            let repo = payload["repo"].as_str().ok_or(StatusCode::BAD_REQUEST)?;
            let input = CopernicusIndexInput {
                repo_url: repo.to_string(),
                index_path: "~/Code/Vault/indexes".to_string(),
            };
            let output = copernicus_index(input).map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
            serde_json::to_value(output).unwrap()
        }
        "discover_repo" => {
            let repo = payload["repo"].as_str().ok_or(StatusCode::BAD_REQUEST)?;
            let input = DiscoverRepoInput {
                repo_url: repo.to_string(),
            };
            let output = discover_repo(input).map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
            serde_json::to_value(output).unwrap()
        }
        "system_status" => {
            system_status(serde_json::json!({})).map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?
        }
        "plugin_list" => {
            plugin_list(serde_json::json!({})).map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?
        }
        _ => return Err(StatusCode::NOT_FOUND),
    };
    Ok(Json(json!({ "result": result })))
}

#[tokio::main]
async fn main() {
    let app = Router::new().route("/tools/:tool", post(handle_tool));
    let addr = SocketAddr::from(([127, 0, 0, 1], 3000));
    println!("MCP HTTP server listening on http://{}", addr);
    
    // Use axum's serve method
    axum::serve(
        tokio::net::TcpListener::bind(&addr).await.unwrap(),
        app,
    ).await.unwrap();
}
