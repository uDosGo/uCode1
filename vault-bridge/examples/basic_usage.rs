// Example demonstrating the SQLite-based vault system
use ucode1_vault_bridge::Vault;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Create a temporary directory for the example
    let temp_dir = tempfile::tempdir()?;
    let db_path = temp_dir.path().join("vault.db");
    let base_path = temp_dir.path().to_str().unwrap().to_string();
    
    // Initialize the vault
    let mut vault = Vault::new(db_path.to_str().unwrap(), &base_path);
    
    // Create a workspace (space)
    let space = vault.create_default_space("My Vault", "/tmp/my_vault")?;
    println!("Created space: {} (ID: {})", space.name, space.id);
    
    // Create some documents
    let doc1 = vault.create_document(&space.id, "Document 1", "# Hello World\n\nThis is my first document.", None, false)?;
    println!("Created document: {} (ID: {})", doc1.name, doc1.id);
    
    let doc2 = vault.create_document(&space.id, "Document 2", "# Second Document\n\nThis is another document.", None, false)?;
    println!("Created document: {} (ID: {})", doc2.name, doc2.id);
    
    // List all documents in the space
    let documents = vault.list_documents(&space.id, None)?;
    println!("\nDocuments in space '{}':", space.name);
    for doc in documents {
        println!("- {} (folder: {})", doc.name, doc.folder);
    }
    
    // Retrieve a specific document
    if let Some(doc) = vault.get_document(&doc1.id)? {
        println!("\nRetrieved document '{}':", doc.name);
        println!("Content preview: {}", &doc.schema[..std::cmp::min(50, doc.schema.len())]);
    }
    
    // Update a document
    vault.update_document(&doc1.id, "# Updated Document\n\nThis document has been updated.")?;
    println!("\nUpdated document: {}", doc1.id);
    
    // Get document history
    let history = vault.get_document_history(&doc1.id)?;
    println!("Document history entries: {}", history.len());
    
    // Soft delete a document
    vault.soft_delete_document(&doc1.id)?;
    println!("Soft deleted document: {}", doc1.id);
    
    // Verify it's no longer in the list
    let documents_after_delete = vault.list_documents(&space.id, None)?;
    println!("Documents after deletion: {}", documents_after_delete.len());
    
    // Restore the document
    vault.restore_document(&doc1.id)?;
    println!("Restored document: {}", doc1.id);
    
    // Verify it's back in the list
    let documents_after_restore = vault.list_documents(&space.id, None)?;
    println!("Documents after restoration: {}", documents_after_restore.len());
    
    Ok(())
}
