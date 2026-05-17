"""
ThinUI API Server

A simple HTTP API that provides the ThinUI bridge functionality
to the frontend via REST endpoints.

This allows the React frontend to communicate with the Python core.

Usage:
    python3 -m core_py.thinui.api
    
Endpoints:
    GET  /api/thinui/health       - Health check
    POST /api/thinui/parse        - Parse ASCII grid text
    POST /api/thinui/render       - Render grid to ThinUI format
    POST /api/thinui/map          - Map grid components
    GET  /api/thinui/project/{id} - Get project by ID
    POST /api/thinui/project      - Save project
"""

import sys
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Ensure uCode1 is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from core_py.thinui import ThinUIGridBridge, ThinUIGridData
from core_py.thinui.formats import ThinUILayout, ThinUIComponent, ThinUIComponentType
from core_py.udo_runtime.api import create_udo_blueprint

# Project storage (in-memory for now)
_PROJECTS: Dict[str, Any] = {}


def create_api_server(host: str = "127.0.0.1", port: int = 8001):
    """Create and configure the API server"""
    try:
        from flask import Flask, request, jsonify, Response
    except ImportError:
        print("Error: Flask not installed. Install with: pip install flask")
        return None
    
    app = Flask(__name__)
    
    # Register UDO blueprint
    app.register_blueprint(create_udo_blueprint())
    
    # Initialize bridge
    bridge = ThinUIGridBridge()
    
    @app.route('/api/thinui/health', methods=['GET'])
    def health():
        """Health check endpoint"""
        return jsonify({
            'status': 'ok',
            'message': 'ThinUI API is running',
            'version': '0.1.0'
        })
    
    @app.route('/api/thinui/parse', methods=['POST'])
    def parse_grid():
        """
        Parse ASCII grid text and return ThinUI format.
        
        Request body:
        {
            "text": "┌───┐\n│ A │\n└───┘",
            "title": "My Grid"
        }
        
        Response:
        ThinUIGridData as JSON
        """
        try:
            data = request.get_json()
            if not data or 'text' not in data:
                return jsonify({'error': 'Missing text parameter'}), 400
            
            text = data['text']
            title = data.get('title', 'Untitled')
            
            # Parse to ThinUI format
            result = bridge.parse_to_thinui(text, title)
            
            return jsonify(result.to_dict())
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/thinui/from-file', methods=['POST'])
    def parse_grid_file():
        """
        Parse ASCII grid from file.
        
        Request body:
        {
            "filepath": "/path/to/grid.txt"
        }
        """
        try:
            data = request.get_json()
            if not data or 'filepath' not in data:
                return jsonify({'error': 'Missing filepath parameter'}), 400
            
            filepath = Path(data['filepath'])
            if not filepath.exists():
                return jsonify({'error': f'File not found: {filepath}'}), 404
            
            # Read file
            text = filepath.read_text()
            title = filepath.stem
            
            # Parse to ThinUI format
            result = bridge.parse_to_thinui(text, title)
            
            return jsonify(result.to_dict())
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/thinui/render', methods=['POST'])
    def render_grid():
        """
        Render ParsedGrid to ThinUI format.
        
        Request body:
        {
            "cells": [[{"char": "A"}, {"char": "B"}], ...],
            "rows": 3,
            "cols": 3,
            "title": "My Grid"
        }
        
        Response:
        ThinUIGridData as JSON
        """
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Missing data'}), 400
            
            # Convert from dict to ThinUIGridData, then back to dict
            # This validates the structure
            grid_data = ThinUIGridData(**data)
            
            return jsonify(grid_data.to_dict())
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/thinui/map', methods=['POST'])
    def map_components():
        """
        Map parsed grid components to ThinUI format.
        
        Request body:
        {
            "cells": [[{"char": "A", "componentId": "btn1"}, ...], ...],
            "rows": 3,
            "cols": 3,
            "components": [{"id": "btn1", "type": "button", ...}],
            "title": "My Mapped Grid"
        }
        """
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Missing data'}), 400
            
            grid_data = ThinUIGridData(**data)
            
            # Map components
            result = bridge.map_to_thinui(
                bridge.parsed_grid_to_thinui(
                    bridge.parser.parse_grid(
                        '\n'.join([''.join(row) for row in data.get('text', [])]),
                        data.get('title', 'Mapped Grid')
                    )
                )
            )
            
            return jsonify(result.to_dict())
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/thinui/tree', methods=['POST'])
    def component_tree():
        """
        Generate ThinUI component tree from grid.
        
        Request body:
        {
            "text": "┌───┐\n│ A │\n└───┘",
            "title": "Component Tree"
        }
        
        Response:
        ThinUIComponent tree as JSON
        """
        try:
            data = request.get_json()
            if not data or 'text' not in data:
                return jsonify({'error': 'Missing text parameter'}), 400
            
            text = data['text']
            title = data.get('title', 'Component Tree')
            
            # Parse and create component tree
            parsed = bridge.parser.parse_grid(text, title)
            tree = bridge.create_thinui_component_tree(parsed)
            
            return jsonify(tree.to_dict())
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/thinui/layout', methods=['POST'])
    def create_layout():
        """
        Create ThinUI layout from grid.
        
        Request body:
        {
            "text": "┌───┐\n│ A │\n└───┘",
            "title": "Layout"
        }
        
        Response:
        ThinUILayout as JSON
        """
        try:
            data = request.get_json()
            if not data or 'text' not in data:
                return jsonify({'error': 'Missing text parameter'}), 400
            
            text = data['text']
            title = data.get('title', 'Layout')
            
            # Parse and create layout
            parsed = bridge.parser.parse_grid(text, title)
            layout = ThinUILayout.from_parsed_grid(parsed)
            
            return jsonify(layout.to_dict())
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/thinui/project/<project_id>', methods=['GET'])
    def get_project(project_id: str):
        """Get a saved project by ID"""
        if project_id not in _PROJECTS:
            return jsonify({'error': f'Project not found: {project_id}'}), 404
        
        return jsonify(_PROJECTS[project_id])
    
    @app.route('/api/thinui/project/<project_id>', methods=['DELETE'])
    def delete_project(project_id: str):
        """Delete a saved project"""
        if project_id not in _PROJECTS:
            return jsonify({'error': f'Project not found: {project_id}'}), 404
        
        del _PROJECTS[project_id]
        return jsonify({'status': 'ok', 'message': f'Deleted project: {project_id}'})
    
    @app.route('/api/thinui/projects', methods=['GET'])
    def list_projects():
        """List all saved projects"""
        return jsonify({
            'status': 'ok',
            'projects': list(_PROJECTS.keys())
        })
    
    @app.route('/api/thinui/project', methods=['POST'])
    def save_project():
        """Save a project"""
        try:
            data = request.get_json()
            if not data or 'id' not in data:
                return jsonify({'error': 'Missing project ID'}), 400
            
            project_id = data['id']
            _PROJECTS[project_id] = data
            
            return jsonify({
                'status': 'ok',
                'message': f'Saved project: {project_id}'
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app


def run_api_server(host: str = "127.0.0.1", port: int = 8001):
    """Run the ThinUI API server"""
    try:
        from flask import Flask
    except ImportError:
        print("Error: Flask not installed. Install with: pip install flask")
        return None
    
    app = create_api_server(host, port)
    
    print(f"Starting ThinUI API server on http://{host}:{port}")
    print(f"Available endpoints:")
    print(f"  GET  http://{host}:{port}/api/thinui/health")
    print(f"  POST http://{host}:{port}/api/thinui/parse")
    print(f"  POST http://{host}:{port}/api/thinui/render")
    print(f"  POST http://{host}:{port}/api/thinui/map")
    print(f"  POST http://{host}:{port}/api/thinui/tree")
    print(f"  POST http://{host}:{port}/api/thinui/layout")
    print(f"  GET  http://{host}:{port}/api/thinui/projects")
    print(f"  POST http://{host}:{port}/api/thinui/project")
    print(f"  UDO Runtime endpoints at /api/udo/*")
    print(f"  GET  http://{host}:{port}/api/udo/health")
    print(f"  GET  http://{host}:{port}/api/udo/skills")
    print(f"  GET  http://{host}:{port}/api/udo/tasks")
    print(f"  GET  http://{host}:{port}/api/udo/variables")
    print(f"  GET  http://{host}:{port}/api/udo/agents")
    print(f"  GET  http://{host}:{port}/api/udo/workflows")
    print(f"  GET  http://{host}:{port}/api/udo/publish/targets")
    print(f"  GET  http://{host}:{port}/api/udo/vault")
    print(f"  GET  http://{host}:{port}/api/udo/mcp/status")
    print(f"  GET  http://{host}:{port}/api/udo/checks")
    print(f"  POST http://{host}:{port}/api/udo/exec")
    
    app.run(host=host, port=port, debug=True)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ThinUI API Server')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8001, help='Port to listen on')
    
    args = parser.parse_args()
    run_api_server(args.host, args.port)


if __name__ == '__main__':
    main()
