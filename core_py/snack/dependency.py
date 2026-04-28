#!/usr/bin/env python3
"""
Snack dependency resolution - Python Implementation

This module provides functionality for resolving Snack dependencies
and managing execution order based on dependency graphs.
"""

from typing import List, Dict, Set, Optional
from collections import defaultdict, deque

from .models import Snack
from .exceptions import CircularDependencyError


class DependencyResolver:
    """Resolve Snack dependencies and determine execution order"""
    
    def __init__(self):
        pass
    
    def resolve_dependencies(self, snacks: List[Snack]) -> List[Snack]:
        """
        Resolve dependencies and return snacks in execution order.
        
        Args:
            snacks: List of Snack objects
            
        Returns:
            List of Snacks in execution order
            
        Raises:
            CircularDependencyError: If circular dependencies are detected
        """
        # Build dependency graph
        graph = self._build_dependency_graph(snacks)
        
        # Perform topological sort
        try:
            execution_order = self._topological_sort(graph)
            
            # Map snack IDs to Snack objects
            snack_map = {snack.id: snack for snack in snacks}
            
            # Return snacks in execution order
            return [snack_map[snack_id] for snack_id in execution_order]
        except CircularDependencyError:
            # Try to identify the cycle
            cycle = self._find_cycle(graph)
            if cycle:
                raise CircularDependencyError(
                    f"Circular dependency detected: {' -> '.join(cycle)}"
                )
            else:
                raise CircularDependencyError("Circular dependency detected")
    
    def _build_dependency_graph(self, snacks: List[Snack]) -> Dict[str, Set[str]]:
        """Build a dependency graph from snacks"""
        graph = defaultdict(set)
        
        # Create nodes for all snacks
        for snack in snacks:
            graph[snack.id] = set()
        
        # Add dependency edges - if A requires B, then B must come before A
        # In topological sort, we need edges to point from dependencies to dependents
        # So if A requires B, we add edge B -> A (B must come before A)
        for snack in snacks:
            for dependency_id in snack.requires:
                if dependency_id in graph:
                    graph[dependency_id].add(snack.id)  # Reverse direction
        
        return graph
    
    def _topological_sort(self, graph: Dict[str, Set[str]]) -> List[str]:
        """Perform topological sort using Kahn's algorithm"""
        # Calculate in-degree for each node
        in_degree = defaultdict(int)
        for node in graph:
            in_degree[node] = 0
        
        for node in graph:
            for neighbor in graph[node]:
                in_degree[neighbor] += 1
        
        # Initialize queue with nodes having 0 in-degree
        queue = deque([node for node in in_degree if in_degree[node] == 0])
        
        result = []
        
        while queue:
            node = queue.popleft()
            result.append(node)
            
            # Reduce in-degree of neighbors
            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # Check for cycles
        if len(result) != len(graph):
            raise CircularDependencyError("Circular dependency detected")
        
        return result
    
    def _find_cycle(self, graph: Dict[str, Set[str]]) -> Optional[List[str]]:
        """Find a cycle in the dependency graph using DFS"""
        visited = set()
        recursion_stack = set()
        parent = {}
        cycle = []
        
        def dfs(node):
            nonlocal cycle
            visited.add(node)
            recursion_stack.add(node)
            
            for neighbor in graph[node]:
                if neighbor not in visited:
                    parent[neighbor] = node
                    dfs(neighbor)
                elif neighbor in recursion_stack:
                    # Found a cycle
                    cycle = [neighbor]
                    current = node
                    while current != neighbor:
                        cycle.append(current)
                        current = parent[current]
                    cycle.append(neighbor)  # Complete the cycle
                    cycle.reverse()
                    return True
            
            recursion_stack.remove(node)
            return False
        
        for node in graph:
            if node not in visited:
                if dfs(node):
                    return cycle
        
        return None
    
    def get_dependency_tree(self, snack_id: str, snacks: List[Snack]) -> Dict[str, List[str]]:
        """Get the dependency tree for a specific snack"""
        snack_map = {snack.id: snack for snack in snacks}
        
        if snack_id not in snack_map:
            raise ValueError(f"Snack not found: {snack_id}")
        
        tree = {}
        visited = set()
        
        def build_tree(current_id: str):
            if current_id in visited:
                return []
            visited.add(current_id)
            
            current_snack = snack_map[current_id]
            dependencies = []
            
            for dep_id in current_snack.requires:
                if dep_id in snack_map:
                    sub_deps = build_tree(dep_id)
                    dependencies.append(dep_id)
                    if sub_deps:
                        dependencies.extend(sub_deps)
            
            return dependencies
        
        tree[snack_id] = build_tree(snack_id)
        return tree


def resolve_snack_dependencies(snacks: List[Snack]) -> List[Snack]:
    """Convenience function to resolve Snack dependencies"""
    resolver = DependencyResolver()
    return resolver.resolve_dependencies(snacks)


# Test the dependency resolver
if __name__ == "__main__":
    print("Testing Snack Dependency Resolver...")
    
    # Create test snacks
    snack_a = Snack.create("A", "Snack A", "1.0.0", "echo 'A'")
    snack_b = Snack.create("B", "Snack B", "1.0.0", "echo 'B'")
    snack_c = Snack.create("C", "Snack C", "1.0.0", "echo 'C'")
    
    # Set up dependencies: A -> B -> C
    snack_b.requires = ["A"]
    snack_c.requires = ["B"]
    
    snacks = [snack_a, snack_b, snack_c]
    
    # Test dependency resolution
    try:
        execution_order = resolve_snack_dependencies(snacks)
        order_ids = [s.id for s in execution_order]
        print(f"✓ Dependency resolution successful: {' -> '.join(order_ids)}")
        
        # The topological sort returns nodes with no dependencies first
        # So the execution order should be A -> B -> C
        # But the sort returns them in reverse dependency order
        expected = ['A', 'B', 'C']
        if order_ids == expected:
            print("✓ Execution order is correct")
        else:
            print(f"✗ Expected {expected}, got {order_ids}")
            print("Note: This might be correct if the algorithm returns execution-ready order")
    except Exception as e:
        print(f"✗ Dependency resolution failed: {e}")
    
    # Test circular dependency detection
    try:
        # Create circular dependency: A -> B -> A
        circular_a = Snack.create("CIRC-A", "Circular A", "1.0.0", "echo 'A'")
        circular_b = Snack.create("CIRC-B", "Circular B", "1.0.0", "echo 'B'")
        circular_a.requires = ["CIRC-B"]
        circular_b.requires = ["CIRC-A"]
        
        circular_snacks = [circular_a, circular_b]
        resolve_snack_dependencies(circular_snacks)
        print("✗ Circular dependency should have been detected")
    except CircularDependencyError as e:
        print(f"✓ Circular dependency correctly detected: {e}")
    
    # Test dependency tree
    try:
        resolver = DependencyResolver()
        tree = resolver.get_dependency_tree("C", snacks)
        print(f"✓ Dependency tree for C: {tree}")
    except Exception as e:
        print(f"✗ Dependency tree failed: {e}")
    
    print("Dependency resolver tests completed!")