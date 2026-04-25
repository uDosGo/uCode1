// src/mcp/tools/copernicus_index.rs
use serde::{Deserialize, Serialize};
use std::fs;
use std::path::Path;
use std::process::Command;

#[derive(Debug, Serialize, Deserialize)]
pub struct CopernicusIndexInput {
    pub repo_url: String,
    pub index_path: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CopernicusIndexOutput {
    pub success: bool,
    pub message: String,
    pub index_path: String,
}

pub fn copernicus_index(input: CopernicusIndexInput) -> Result<CopernicusIndexOutput, String> {
    let index_dir = Path::new(&input.index_path);
    if !index_dir.exists() {
        fs::create_dir_all(index_dir)
            .map_err(|e| format!("Failed to create index directory: {}", e))?;
    }

    let repo_name = input
        .repo_url
        .split('/')
        .last()
        .ok_or("Invalid repo URL")?
        .replace(".git", "");
    let repo_path = index_dir.join(&repo_name);

    if repo_path.exists() {
        fs::remove_dir_all(&repo_path)
            .map_err(|e| format!("Failed to remove existing repo: {}", e))?;
    }

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

    let db_path = index_dir.join(format!("{}.db", repo_name));
    let script_content = format!(
        "#!/usr/bin/env python3\\nimport sqlite3\\nimport os\\nimport json\\nfrom pathlib import Path\\n\\nrepo_path = '{}'\\ndb_path = '{}'\\n\\nconn = sqlite3.connect(db_path)\\nc = conn.cursor()\\n\\nc.execute('''CREATE TABLE IF NOT EXISTS files (id INTEGER PRIMARY KEY, path TEXT, content TEXT)''')\\nc.execute('''CREATE TABLE IF NOT EXISTS symbols (id INTEGER PRIMARY KEY, name TEXT, type TEXT, file_id INTEGER)''')\\n\\nfor root, _, files in os.walk(repo_path):\\n    for file in files:\\n        if file.endswith('.rs'):\\n            file_path = os.path.join(root, file)\\n            with open(file_path, 'r') as f:\\n                content = f.read()\\n            c.execute('INSERT INTO files (path, content) VALUES (?, ?)', (file_path, content))\\n\\nconn.commit()\\nconn.close()\\nprint('Index created successfully')\\n",
        repo_path.to_str().unwrap(),
        db_path.to_str().unwrap()
    );

    let script_path = index_dir.join("index.py");
    fs::write(&script_path, script_content)
        .map_err(|e| format!("Failed to write index script: {}", e))?;

    let index_output = Command::new("python3")
        .arg(script_path)
        .current_dir(index_dir)
        .output()
        .map_err(|e| format!("Failed to run index script: {}", e))?;

    if !index_output.status.success() {
        return Err(format!(
            "Failed to create index: {}",
            String::from_utf8_lossy(&index_output.stderr)
        ));
    }

    Ok(CopernicusIndexOutput {
        success: true,
        message: "Index created successfully".to_string(),
        index_path: db_path.to_str().unwrap().to_string(),
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::tempdir;

    #[test]
    fn test_copernicus_index_invalid_url() {
        let input = CopernicusIndexInput {
            repo_url: "invalid-url".to_string(),
            index_path: tempdir().unwrap().path().to_str().unwrap().to_string(),
        };
        let result = copernicus_index(input);
        assert!(result.is_err());
    }
}