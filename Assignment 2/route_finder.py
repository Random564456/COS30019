import sys
from collections import deque, defaultdict
import re

# Read Data from the input CMI
def read_graph(filename):
    with open(filename, 'r') as f:
        content = f.read()
    
    # Parse main sections
    sections = {}
    section_names = ["Nodes:", "Edges:", "Origin:", "Destinations:"]
    current_section = None
    section_content = []
    
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line in section_names:
            if current_section:
                sections[current_section] = '\n'.join(section_content)
            current_section = line
            section_content = []
        elif current_section:
            section_content.append(line)
    
    # Add the last section
    if current_section and section_content:
        sections[current_section] = '\n'.join(section_content)
    
    # Extract nodes
    nodes = set()
    if "Nodes:" in sections:
        node_lines = sections["Nodes:"].split('\n')
        for line in node_lines:
            if ":" in line:
                node_id = line.split(":")[0].strip()
                nodes.add(node_id)
    
    # Extract edges
    edges = defaultdict(list)
    if "Edges:" in sections:
        edge_lines = sections["Edges:"].split('\n')
        for line in edge_lines:
            match = re.match(r'^\((\d+),(\d+)\):\s*\d+$', line)
            if match:
                a, b = match.group(1), match.group(2)
                # treat edges as undirected
                if b not in edges[a]:
                    edges[a].append(b)
                if a not in edges[b]:
                    edges[b].append(a)
    
    # Sort edges for tie-breaking
    for node in edges:
        edges[node] = sorted(edges[node], key=lambda x: int(x))
    
    # Extract origin
    origin = None
    if "Origin:" in sections:
        origin_text = sections["Origin:"].strip()
        if origin_text:
            origin = origin_text
    
    # Extract destinations
    destinations = set()
    if "Destinations:" in sections:
        dest_text = sections["Destinations:"].strip()
        if dest_text:
            # Split by semicolon
            for part in dest_text.split(';'):
                part = part.strip()
                if part:
                    # Take only the first word in case there are comments
                    dest = part.split()[0].strip()
                    destinations.add(dest)
    
    return nodes, edges, origin, destinations

# ---------------------------------------------------------------------------------

# BFS Algorithm
def bfs(edges, origin, destinations):
    if not origin:
        return None, 0, []  # No origin to start from
    
    # Convert to strings to ensure consistent comparisons
    origin = str(origin)
    destinations = {str(d) for d in destinations}
    
    frontier = deque([[origin]])
    explored = set()
    nodes_examined = 0

    while frontier:
        path = frontier.popleft()
        current = path[-1]
        nodes_examined += 1
        
        # Check if we've reached a destination
        if current in destinations:
            return current, nodes_examined, path
            
        # Mark as explored after checking destination
        explored.add(current)
        
        # Add unvisited neighbors to frontier
        for neighbor in edges.get(current, []):
            if neighbor not in explored and not any(neighbor == p[-1] for p in frontier):
                new_path = path + [neighbor]
                frontier.append(new_path)

    return None, nodes_examined, []

# ----------------------------------------------------------------------------------

def bi_directional_bfs(edges, origin, destinations):
    if not origin or not destinations:
        return None, 0, []  # No origin or destinations to start from
    
    origin = str(origin)
    destinations = {str(d) for d in destinations}
    
    # Choose a single destination for the backward search
    dest = list(destinations)[0]  # For bidirectional, start with one destination
    
    # Frontiers for origin and destination
    origin_frontier = deque([origin])
    dest_frontier = deque([dest])
    
    # Paths to track how we got to each node
    origin_paths = {origin: [origin]}
    dest_paths = {dest: [dest]}
    
    # Explored sets to track visited nodes from both sides
    explored_origin = set([origin])
    explored_dest = set([dest])
    
    nodes_examined = 0
    
    while origin_frontier and dest_frontier:
        # Expand from the origin side
        current = origin_frontier.popleft()
        nodes_examined += 1
        
        # Check if current node has been visited from destination side
        if current in explored_dest:
            # We found where the two searches meet
            forward_path = origin_paths[current]
            backward_path = dest_paths[current]
            # Remove the duplicate meeting point
            backward_path.pop(0)
            backward_path.reverse()
            full_path = forward_path + backward_path
            return current, nodes_examined, full_path
        
        # Expand neighbors from origin side
        for neighbor in edges.get(current, []):
            if neighbor not in explored_origin:
                explored_origin.add(neighbor)
                origin_frontier.append(neighbor)
                origin_paths[neighbor] = origin_paths[current] + [neighbor]
                
                # Check if this new node is in destination's explored set
                if neighbor in explored_dest:
                    forward_path = origin_paths[neighbor]
                    backward_path = dest_paths[neighbor]
                    backward_path.pop(0)  # Remove duplicate meeting point
                    backward_path.reverse()
                    full_path = forward_path + backward_path
                    return neighbor, nodes_examined, full_path
        
        # Expand from the destination side
        current = dest_frontier.popleft()
        nodes_examined += 1
        
        # Check if current node has been visited from origin side
        if current in explored_origin:
            # We found where the two searches meet
            forward_path = origin_paths[current]
            backward_path = dest_paths[current]
            backward_path.pop(0)  # Remove duplicate meeting point
            backward_path.reverse()
            full_path = forward_path + backward_path
            return current, nodes_examined, full_path
        
        # Expand neighbors from destination side
        for neighbor in edges.get(current, []):
            if neighbor not in explored_dest:
                explored_dest.add(neighbor)
                dest_frontier.append(neighbor)
                dest_paths[neighbor] = dest_paths[current] + [neighbor]
                
                # Check if this new node is in origin's explored set
                if neighbor in explored_origin:
                    forward_path = origin_paths[neighbor]
                    backward_path = dest_paths[neighbor]
                    backward_path.pop(0)  # Remove duplicate meeting point
                    backward_path.reverse()
                    full_path = forward_path + backward_path
                    return neighbor, nodes_examined, full_path
    
    # Check all other destinations if bidirectional didn't work with first destination
    for dest in destinations:
        if dest in explored_origin:
            return dest, nodes_examined, origin_paths[dest]
    
    return None, nodes_examined, []
    
    
    

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 route_finder.py <filename> BFS")
        return

    filename = sys.argv[1]
    method = sys.argv[2].upper()

    nodes, edges, origin, destinations = read_graph(filename)
    
    if (method == "BFS"):
        goal, nodes_created, path = bfs(edges, origin, destinations)   
    elif (method == "CUS1"):
        goal, nodes_created, path = bi_directional_bfs(edges, origin, destinations)     
    else:
        print(f'Search Tree Method {method} defined is not handled')
        return



    if goal:
        print(f"{filename} {method} {goal} {nodes_created} {' '.join(path)}")
    else:
        print(f"{filename} {method} NoPath {nodes_created}")

if __name__ == "__main__":
    main()