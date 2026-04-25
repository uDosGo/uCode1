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
use log::error;

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
            // Run blocking function in a separate thread
            let output = tokio::task::spawn_blocking(move || {
                spark_launch(input)
            }).await;
            let output = match output {
                Ok(Ok(val)) => val,
                Ok(Err(e)) => {
                    error!("spark_launch failed: {}", e);
                    return Err(StatusCode::INTERNAL_SERVER_ERROR);
                }
                Err(e) => {
                    error!("spark_launch task failed: {:?}", e);
                    return Err(StatusCode::INTERNAL_SERVER_ERROR);
                }
            };
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
            let output = tokio::task::spawn_blocking(move || {
                agentic_workflow_create(input)
            }).await;
            let output = match output {
                Ok(Ok(val)) => val,
                Ok(Err(e)) => {
                    error!("agentic_workflow_create failed: {}", e);
                    return Err(StatusCode::INTERNAL_SERVER_ERROR);
                }
                Err(e) => {
                    error!("agentic_workflow_create task failed: {:?}", e);
                    return Err(StatusCode::INTERNAL_SERVER_ERROR);
                }
            };
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
            let output = tokio::task::spawn_blocking(move || {
                flat_data_schedule(input)
            }).await;
            let output = match output {
                Ok(Ok(val)) => val,
                Ok(Err(e)) => {
                    error!("flat_data_schedule failed: {}", e);
                    return Err(StatusCode::INTERNAL_SERVER_ERROR);
                }
                Err(e) => {
                    error!("flat_data_schedule task failed: {:?}", e);
                    return Err(StatusCode::INTERNAL_SERVER_ERROR);
                }
            };
            serde_json::to_value(output).unwrap()
        }
        "copernicus_index" => {
            let repo = payload["repo"].as_str().ok_or(StatusCode::BAD_REQUEST)?;
            let input = CopernicusIndexInput {
                repo_url: repo.to_string(),
                index_path: "~/Code/Vault/indexes".to_string(),
            };
            let output = tokio::task::spawn_blocking(move || {
                copernicus_index(input)
            }).await;
            let output = match output {
                Ok(Ok(val)) => val,
                Ok(Err(e)) => {
                    error!("copernicus_index failed: {}", e);
                    return Err(StatusCode::INTERNAL_SERVER_ERROR);
                }
                Err(e) => {
                    error!("copernicus_index task failed: {:?}", e);
                    return Err(StatusCode::INTERNAL_SERVER_ERROR);
                }
            };
            serde_json::to_value(output).unwrap()
        }
        "discover_repo" => {
            let repo = payload["repo"].as_str().ok_or(StatusCode::BAD_REQUEST)?;
            let input = DiscoverRepoInput {
                repo_url: repo.to_string(),
            };
            let output = tokio::task::spawn_blocking(move || {
                discover_repo(input)
            }).await;
            let output = match output {
                Ok(Ok(val)) => val,
                Ok(Err(e)) => {
                    error!("discover_repo failed: {}", e);
                    return Err(StatusCode::INTERNAL_SERVER_ERROR);
                }
                Err(e) => {
                    error!("discover_repo task failed: {:?}", e);
                    return Err(StatusCode::INTERNAL_SERVER_ERROR);
                }
            };
            serde_json::to_value(output).unwrap()
        }
        "system_status" => {
            let output = tokio::task::spawn_blocking(|| {
                system_status(serde_json::json!({}))
            }).await;
            let output = match output {
                Ok(Ok(val)) => val,
                Ok(Err(e)) => {
                    error!("system_status failed: {}", e);
                    return Err(StatusCode::INTERNAL_SERVER_ERROR);
                }
                Err(e) => {
                    error!("system_status task failed: {:?}", e);
                    return Err(StatusCode::INTERNAL_SERVER_ERROR);
                }
            };
            output
        }
        "plugin_list" => {
            let output = tokio::task::spawn_blocking(|| {
                plugin_list(serde_json::json!({}))
            }).await;
            let output = match output {
                Ok(Ok(val)) => val,
                Ok(Err(e)) => {
                    error!("plugin_list failed: {}", e);
                    return Err(StatusCode::INTERNAL_SERVER_ERROR);
                }
                Err(e) => {
                    error!("plugin_list task failed: {:?}", e);
                    return Err(StatusCode::INTERNAL_SERVER_ERROR);
                }
            };
            output
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
