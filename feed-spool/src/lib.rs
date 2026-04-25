// Feed Spool - RSS/Atom feed processing for uCode1

use std::fs;
use std::path::PathBuf;
use serde::{Serialize, Deserialize};
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FeedItem {
    pub id: String,
    pub title: String,
    pub link: String,
    pub description: Option<String>,
    pub content: Option<String>,
    pub published: Option<String>,  // ISO 8601 format
    pub updated: Option<String>,    // ISO 8601 format
    pub author: Option<String>,
    pub categories: Vec<String>,
    pub read: bool,
    pub starred: bool,
    pub feed_url: String,
}

impl FeedItem {
    pub fn new(feed_url: &str) -> Self {
        FeedItem {
            id: Uuid::new_v4().to_string(),
            title: String::new(),
            link: String::new(),
            description: None,
            content: None,
            published: None,
            updated: None,
            author: None,
            categories: Vec::new(),
            read: false,
            starred: false,
            feed_url: feed_url.to_string(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Feed {
    pub url: String,
    pub title: String,
    pub link: Option<String>,
    pub description: Option<String>,
    pub last_fetched: Option<String>,  // ISO 8601 format
    pub last_updated: Option<String>,   // ISO 8601 format
    pub items: Vec<FeedItem>,
}

impl Feed {
    pub fn new(url: &str) -> Self {
        Feed {
            url: url.to_string(),
            title: String::new(),
            link: None,
            description: None,
            last_fetched: None,
            last_updated: None,
            items: Vec::new(),
        }
    }
}

pub struct FeedSpool {
    spool_dir: PathBuf,
}

impl FeedSpool {
    pub fn new(vault_path: &str) -> Self {
        let spool_dir = PathBuf::from(vault_path).join("feeds");
        FeedSpool { spool_dir }
    }

    pub fn spool_dir(&self) -> &PathBuf {
        &self.spool_dir
    }

    pub fn ensure_directory(&self) -> std::io::Result<()> {
        fs::create_dir_all(&self.spool_dir)?;
        Ok(())
    }

    pub fn add_feed(&self, feed_url: &str) -> std::io::Result<Feed> {
        let feed = Feed::new(feed_url);
        let feed_file = self.spool_dir.join(format!("{}.json", feed_url_to_filename(feed_url)));
        
        let json = serde_json::to_string_pretty(&feed)?;
        fs::write(feed_file, json)?;
        
        Ok(feed)
    }

    pub fn list_feeds(&self) -> std::io::Result<Vec<Feed>> {
        let mut feeds = Vec::new();
        
        if !self.spool_dir.exists() {
            return Ok(feeds);
        }
        
        for entry in fs::read_dir(&self.spool_dir)? {
            let entry = entry?;
            if entry.path().extension().and_then(|s| s.to_str()) == Some("json") {
                let json = fs::read_to_string(entry.path())?;
                if let Ok(feed) = serde_json::from_str::<Feed>(&json) {
                    feeds.push(feed);
                }
            }
        }
        
        Ok(feeds)
    }

    pub fn get_feed(&self, feed_url: &str) -> std::io::Result<Option<Feed>> {
        let feed_file = self.spool_dir.join(format!("{}.json", feed_url_to_filename(feed_url)));
        
        if !feed_file.exists() {
            return Ok(None);
        }
        
        let json = fs::read_to_string(feed_file)?;
        let feed = serde_json::from_str::<Feed>(&json)?;
        
        Ok(Some(feed))
    }

    pub fn update_feed(&self, feed: &Feed) -> std::io::Result<()> {
        let feed_file = self.spool_dir.join(format!("{}.json", feed_url_to_filename(&feed.url)));
        let json = serde_json::to_string_pretty(feed)?;
        fs::write(feed_file, json)?;
        Ok(())
    }

    pub fn remove_feed(&self, feed_url: &str) -> std::io::Result<()> {
        let feed_file = self.spool_dir.join(format!("{}.json", feed_url_to_filename(feed_url)));
        if feed_file.exists() {
            fs::remove_file(feed_file)?;
        }
        Ok(())
    }

    pub fn mark_item_read(&self, feed_url: &str, item_id: &str, read: bool) -> std::io::Result<()> {
        if let Some(mut feed) = self.get_feed(feed_url)? {
            if let Some(item) = feed.items.iter_mut().find(|i| i.id == item_id) {
                item.read = read;
                self.update_feed(&feed)?;
            }
        }
        Ok(())
    }

    pub fn mark_item_starred(&self, feed_url: &str, item_id: &str, starred: bool) -> std::io::Result<()> {
        if let Some(mut feed) = self.get_feed(feed_url)? {
            if let Some(item) = feed.items.iter_mut().find(|i| i.id == item_id) {
                item.starred = starred;
                self.update_feed(&feed)?;
            }
        }
        Ok(())
    }
}

fn feed_url_to_filename(url: &str) -> String {
    url.replace("https://", "")
        .replace("http://", "")
        .replace("/", "_")
        .replace("?", "_")
        .replace("&", "_")
        .replace("=", "_")
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::tempdir;

    #[test]
    fn test_feed_item_creation() {
        let item = FeedItem::new("http://example.com/feed.xml");
        assert!(!item.id.is_empty());
        assert_eq!(item.feed_url, "http://example.com/feed.xml");
    }

    #[test]
    fn test_feed_creation() {
        let feed = Feed::new("http://example.com/feed.xml");
        assert_eq!(feed.url, "http://example.com/feed.xml");
        assert!(feed.items.is_empty());
    }

    #[test]
    fn test_feed_spool_operations() {
        let dir = tempdir().unwrap();
        let vault_path = dir.path().to_str().unwrap();
        let spool = FeedSpool::new(vault_path);
        spool.ensure_directory().unwrap();
        
        // Add a feed
        let feed = spool.add_feed("http://example.com/feed.xml").unwrap();
        assert_eq!(feed.url, "http://example.com/feed.xml");
        
        // List feeds
        let feeds = spool.list_feeds().unwrap();
        assert_eq!(feeds.len(), 1);
        
        // Get feed
        let retrieved_feed = spool.get_feed("http://example.com/feed.xml").unwrap();
        assert!(retrieved_feed.is_some());
        
        // Remove feed
        spool.remove_feed("http://example.com/feed.xml").unwrap();
        let feeds = spool.list_feeds().unwrap();
        assert!(feeds.is_empty());
    }

    #[test]
    fn test_feed_url_to_filename() {
        assert_eq!(
            feed_url_to_filename("https://example.com/feed.xml"),
            "example.com_feed.xml"
        );
        assert_eq!(
            feed_url_to_filename("http://blog.com/rss?param=value"),
            "blog.com_rss_param=value"
        );
    }
}