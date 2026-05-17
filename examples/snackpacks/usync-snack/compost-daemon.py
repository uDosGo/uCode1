#!/usr/bin/env python3
# ~/Code/Dev/Usync/compost-daemon.py

"""
Self-Healing Compost System
Monitors, learns, adapts, heals
"""

import asyncio
import hashlib
import json
import pickle
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import numpy as np
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class CompostIntelligence:
    """The brain of the compost system"""
    
    def __init__(self, compost_path: Path):
        self.compost_path = compost_path
        self.model = self.load_model()
        self.patterns = self.load_patterns()
        self.thresholds = self.load_thresholds()
        self.decision_log = []
        
    async def monitor_loop(self):
        """Main monitoring loop"""
        while True:
            try:
                # Check system health
                health = await self.check_health()
                
                # Detect anomalies
                anomalies = await self.detect_anomalies(health)
                
                # Decide actions
                if anomalies:
                    actions = await self.decide_actions(anomalies)
                    await self.execute_actions(actions)
                
                # Learn from outcomes
                await self.learn(actions)
                
                # Update vector index
                await self.update_vector_index()
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                await self.handle_critical_error(e)
    
    async def check_health(self) -> Dict:
        """Comprehensive health check"""
        return {
            'size_gb': await self.get_size_gb(),
            'file_count': await self.get_file_count(),
            'avg_age_days': await self.get_avg_age(),
            'vector_index_health': await self.check_vector_health(),
            'compression_ratio': await self.get_compression_ratio(),
            'duplicate_rate': await self.get_duplicate_rate(),
            'corruption_rate': await self.get_corruption_rate(),
            'recovery_points': await self.count_recovery_points()
        }
    
    async def detect_anomalies(self, health: Dict) -> List[Dict]:
        """Detect anomalies using ML + rules"""
        anomalies = []
        
        # Rule-based detection
        if health['size_gb'] > self.thresholds['max_size']:
            anomalies.append({
                'type': 'disk_pressure',
                'severity': 'high',
                'value': health['size_gb'],
                'threshold': self.thresholds['max_size']
            })
        
        if health['duplicate_rate'] > self.thresholds['max_duplicates']:
            anomalies.append({
                'type': 'high_duplication',
                'severity': 'medium',
                'value': health['duplicate_rate'],
                'threshold': self.thresholds['max_duplicates']
            })
        
        # ML-based anomaly detection
        ml_anomalies = await self.model.predict_anomalies(health)
        anomalies.extend(ml_anomalies)
        
        # Log for learning
        self.decision_log.append({
            'timestamp': datetime.now().isoformat(),
            'health': health,
            'anomalies': anomalies
        })
        
        return anomalies
    
    async def decide_actions(self, anomalies: List[Dict]) -> List[Dict]:
        """Intelligent action decision"""
        actions = []
        
        for anomaly in anomalies:
            # Use ML model for action selection
            action = await self.model.suggest_action(anomaly)
            
            # Fallback to rules
            if not action:
                action = self.rule_based_action(anomaly)
            
            actions.append({
                'anomaly': anomaly,
                'action': action,
                'priority': anomaly.get('severity', 'medium'),
                'timestamp': datetime.now().isoformat()
            })
        
        # Sort by priority
        actions.sort(key=lambda x: {'high': 0, 'medium': 1, 'low': 2}[x['priority']])
        
        return actions
    
    async def execute_actions(self, actions: List[Dict]):
        """Execute with rollback capability"""
        for action in actions:
            try:
                # Create rollback point
                rollback_id = await self.create_rollback_point()
                
                # Execute action
                result = await self.perform_action(action)
                
                # Verify result
                if not await self.verify_action(result):
                    # Rollback if failed
                    await self.rollback(rollback_id)
                    action['status'] = 'failed_rolled_back'
                else:
                    action['status'] = 'success'
                    action['rollback_id'] = rollback_id
                
            except Exception as e:
                await self.handle_action_failure(action, e)
    
    async def perform_action(self, action: Dict) -> Dict:
        """Execute a specific healing action"""
        action_type = action['action']['type']
        
        if action_type == 'compress':
            return await self.smart_compress()
        
        elif action_type == 'deduplicate':
            return await self.smart_deduplicate()
        
        elif action_type == 'reindex':
            return await self.smart_reindex()
        
        elif action_type == 'repair':
            return await self.smart_repair(action['anomaly'])
        
        elif action_type == 'quarantine':
            return await self.quarantine_corrupted()
        
        else:
            raise ValueError(f"Unknown action: {action_type}")
    
    async def smart_compress(self) -> Dict:
        """Intelligent compression based on content type"""
        files = await self.get_files_by_age()
        compressed = []
        
        for file in files:
            # Detect content type
            content_type = await self.detect_content_type(file)
            
            # Choose algorithm
            algorithms = {
                'text': 'zstd',
                'markdown': 'zstd',
                'json': 'brotli',
                'binary': 'lz4',
                'image': 'webp',
                'vector': 'quantize'  # Lossy but semantic
            }
            
            algo = algorithms.get(content_type, 'zstd')
            level = await self.calculate_compression_level(file)
            
            # Compress
            result = await self.compress_file(file, algo, level)
            compressed.append(result)
        
        return {
            'files_compressed': len(compressed),
            'space_saved_mb': sum(r['saved_mb'] for r in compressed),
            'algorithm_used': algorithms,
            'timestamp': datetime.now().isoformat()
        }
    
    async def smart_deduplicate(self) -> Dict:
        """Semantic deduplication using vectors"""
        duplicates = []
        
        # Get all files with vectors
        vectors = await self.load_all_vectors()
        
        # Find similar clusters
        clusters = await self.cluster_vectors(vectors, threshold=0.95)
        
        for cluster in clusters:
            if len(cluster) > 1:
                # Keep the most recent or most complete
                keeper = await self.select_best_file(cluster)
                duplicates.append({
                    'keeper': keeper,
                    'duplicates': [f for f in cluster if f != keeper],
                    'similarity': cluster['similarity']
                })
        
        # Replace duplicates with symlinks
        for dup in duplicates:
            for duplicate in dup['duplicates']:
                await self.replace_with_symlink(duplicate, dup['keeper'])
        
        return {
            'clusters_found': len(clusters),
            'duplicates_removed': sum(len(d['duplicates']) for d in duplicates),
            'space_saved_mb': await self.calculate_savings(duplicates)
        }
    
    async def smart_reindex(self) -> Dict:
        """Intelligent reindexing with vector preservation"""
        # Check what needs reindexing
        stats = await self.get_index_stats()
        
        if stats['fragmentation'] > 0.4:
            # Full reindex
            await self.full_reindex()
        elif stats['stale_vectors'] > 0.1:
            # Incremental update
            await self.incremental_reindex()
        
        # Optimize vector search
        await self.optimize_vector_search()
        
        return {
            'index_type': 'full' if stats['fragmentation'] > 0.4 else 'incremental',
            'vectors_updated': stats['total_vectors'],
            'new_fragmentation': await self.get_fragmentation()
        }
    
    async def learn(self, actions: List[Dict]):
        """Learn from outcomes to improve future decisions"""
        # Update model with results
        for action in actions:
            outcome = await self.get_action_outcome(action)
            await self.model.update(action, outcome)
        
        # Update patterns
        new_patterns = await self.discover_patterns()
        self.patterns.update(new_patterns)
        
        # Adjust thresholds if needed
        await self.adapt_thresholds()
        
        # Save learning
        await self.save_model()
        await self.save_patterns()

# Placeholder functions for the model and utilities
class DummyModel:
    async def predict_anomalies(self, health):
        return []
    
    async def suggest_action(self, anomaly):
        return {'type': 'compress'}
    
    async def update(self, action, outcome):
        pass

# Initialize and run the daemon
if __name__ == "__main__":
    compost_path = Path("/Users/fredbook/uDosGo/Memory/State/Compost")
    daemon = CompostIntelligence(compost_path)
    asyncio.run(daemon.monitor_loop())