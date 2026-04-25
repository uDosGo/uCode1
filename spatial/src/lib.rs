// Spatial Index - 2D vector index and maps for uCode1

use std::collections::HashMap;
use geo::Point;
use rstar::{RTree, AABB, PointDistance, RTreeObject};
use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
struct SerializablePoint {
    x: f64,
    y: f64,
}

impl From<Point<f64>> for SerializablePoint {
    fn from(point: Point<f64>) -> Self {
        SerializablePoint {
            x: point.x(),
            y: point.y(),
        }
    }
}

impl From<SerializablePoint> for Point<f64> {
    fn from(sp: SerializablePoint) -> Self {
        Point::new(sp.x, sp.y)
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SpatialPoint {
    pub id: String,
    #[serde(with = "serializable_point")]
    pub point: Point<f64>,
    pub properties: HashMap<String, String>,
}

mod serializable_point {
    use super::*;
    use serde::{Serializer, Deserializer};

    pub fn serialize<S>(point: &Point<f64>, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        let sp: SerializablePoint = (*point).into();
        sp.serialize(serializer)
    }

    pub fn deserialize<'de, D>(deserializer: D) -> Result<Point<f64>, D::Error>
    where
        D: Deserializer<'de>,
    {
        let sp = SerializablePoint::deserialize(deserializer)?;
        Ok(sp.into())
    }
}

impl RTreeObject for SpatialPoint {
    type Envelope = AABB<[f64; 2]>;

    fn envelope(&self) -> Self::Envelope {
        AABB::from_point([self.point.x(), self.point.y()])
    }
}

impl PointDistance for SpatialPoint {
    fn distance_2(&self, point: &[f64; 2]) -> f64 {
        let dx = self.point.x() - point[0];
        let dy = self.point.y() - point[1];
        dx * dx + dy * dy
    }
}

pub struct SpatialIndex {
    rtree: RTree<SpatialPoint>,
}

impl SpatialIndex {
    pub fn new() -> Self {
        SpatialIndex {
            rtree: RTree::new(),
        }
    }

    pub fn add_point(&mut self, point: SpatialPoint) {
        self.rtree.insert(point);
    }

    pub fn nearest_points(&self, point: &Point<f64>, radius: f64) -> Vec<&SpatialPoint> {
        let center = [point.x(), point.y()];
        let _aabb = AABB::from_point(center);
        
        self.rtree
            .locate_within_distance(center, radius)
            .collect()
    }

    pub fn points_in_bounds(&self, min_x: f64, min_y: f64, max_x: f64, max_y: f64) -> Vec<&SpatialPoint> {
        let aabb = AABB::from_corners([min_x, min_y], [max_x, max_y]);
        self.rtree.locate_in_envelope(&aabb).collect()
    }

    pub fn all_points(&self) -> Vec<&SpatialPoint> {
        self.rtree.iter().collect()
    }

    pub fn save_to_file(&self, path: &str) -> std::io::Result<()> {
        let points: Vec<&SpatialPoint> = self.all_points();
        let json = serde_json::to_string(&points)?;
        std::fs::write(path, json)?;
        Ok(())
    }

    pub fn load_from_file(&mut self, path: &str) -> std::io::Result<()> {
        let json = std::fs::read_to_string(path)?;
        let points: Vec<SpatialPoint> = serde_json::from_str(&json)?;
        
        for point in points {
            self.add_point(point);
        }
        
        Ok(())
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MapLayer {
    pub name: String,
    pub points: Vec<SpatialPoint>,
}

pub struct MapManager {
    layers: HashMap<String, MapLayer>,
    spatial_index: SpatialIndex,
}

impl MapManager {
    pub fn new() -> Self {
        MapManager {
            layers: HashMap::new(),
            spatial_index: SpatialIndex::new(),
        }
    }

    pub fn add_layer(&mut self, layer: MapLayer) {
        self.layers.insert(layer.name.clone(), layer);
    }

    pub fn get_layer(&self, name: &str) -> Option<&MapLayer> {
        self.layers.get(name)
    }

    pub fn add_point_to_layer(&mut self, layer_name: &str, point: SpatialPoint) {
        if let Some(layer) = self.layers.get_mut(layer_name) {
            layer.points.push(point.clone());
        } else {
            let mut new_layer = MapLayer {
                name: layer_name.to_string(),
                points: Vec::new(),
            };
            new_layer.points.push(point.clone());
            self.layers.insert(layer_name.to_string(), new_layer);
        }
        
        self.spatial_index.add_point(point);
    }

    pub fn nearest_points(&self, point: &Point<f64>, radius: f64) -> Vec<&SpatialPoint> {
        self.spatial_index.nearest_points(point, radius)
    }

    pub fn save_to_directory(&self, dir_path: &str) -> std::io::Result<()> {
        std::fs::create_dir_all(dir_path)?;
        
        for (layer_name, layer) in &self.layers {
            let layer_path = format!("{}/{}.json", dir_path, layer_name);
            let json = serde_json::to_string(layer)?;
            std::fs::write(layer_path, json)?;
        }
        
        Ok(())
    }

    pub fn load_from_directory(&mut self, dir_path: &str) -> std::io::Result<()> {
        if let Ok(entries) = std::fs::read_dir(dir_path) {
            for entry in entries {
                if let Ok(entry) = entry {
                    if let Some(ext) = entry.path().extension() {
                        if ext == "json" {
                            if let Some(_layer_name) = entry.path().file_stem() {
                                let json = std::fs::read_to_string(entry.path())?;
                                if let Ok(layer) = serde_json::from_str::<MapLayer>(&json) {
                                    self.add_layer(layer.clone());
                                    for point in &layer.points {
                                        self.spatial_index.add_point(point.clone());
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_spatial_index() {
        let mut index = SpatialIndex::new();
        
        let point1 = SpatialPoint {
            id: "p1".to_string(),
            point: Point::new(0.0, 0.0),
            properties: HashMap::new(),
        };
        
        let point2 = SpatialPoint {
            id: "p2".to_string(),
            point: Point::new(1.0, 1.0),
            properties: HashMap::new(),
        };
        
        index.add_point(point1.clone());
        index.add_point(point2.clone());
        
        let query_point = Point::new(0.1, 0.1);
        let nearest = index.nearest_points(&query_point, 0.5);
        
        assert_eq!(nearest.len(), 1);
        assert_eq!(nearest[0].id, "p1");
    }

    #[test]
    fn test_map_manager() {
        let mut manager = MapManager::new();
        
        let point = SpatialPoint {
            id: "test".to_string(),
            point: Point::new(10.0, 20.0),
            properties: HashMap::new(),
        };
        
        manager.add_point_to_layer("locations", point.clone());
        
        assert!(manager.get_layer("locations").is_some());
        let nearest = manager.nearest_points(&Point::new(10.1, 20.1), 1.0);
        assert_eq!(nearest.len(), 1);
    }

    #[test]
    fn test_save_load() {
        use tempfile::tempdir;
        
        let dir = tempdir().unwrap();
        let dir_path = dir.path();
        
        let mut manager = MapManager::new();
        
        let point = SpatialPoint {
            id: "save_test".to_string(),
            point: Point::new(5.0, 5.0),
            properties: HashMap::new(),
        };
        
        manager.add_point_to_layer("test_layer", point);
        manager.save_to_directory(dir_path.to_str().unwrap()).unwrap();
        
        let mut new_manager = MapManager::new();
        new_manager.load_from_directory(dir_path.to_str().unwrap()).unwrap();
        
        assert!(new_manager.get_layer("test_layer").is_some());
    }
}