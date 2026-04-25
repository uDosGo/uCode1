// Schema definitions for SQLite database
use serde::{Serialize, Deserialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct Space {
    pub id: String,
    pub name: String,
    pub write_folder_path: String,
    pub sort: i32,
    pub opt: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Doc {
    pub id: String,
    pub name: String,
    pub space_id: String,
    pub parent_id: Option<String>,
    pub folder: bool,
    pub schema: String,
    pub links: Option<String>,
    pub medias: Option<String>,
    pub sort: i32,
    pub deleted: bool,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct History {
    pub id: i64,
    pub doc_id: String,
    pub schema: String,
    pub created: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Link {
    pub target: String,
    pub link_type: String,
    pub line: i32,
}
