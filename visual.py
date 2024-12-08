import json

# Load the JSON file
with open('org_structure.json', 'r') as file:
    tree_data = json.load(file)

# Ensure the JSON data is loaded correctly
if not isinstance(tree_data, dict):
    raise ValueError("The JSON data should be a dictionary representing the tree structure.")

def parse_tree(tree, parent=None):
    """
    Recursively parse the tree and return a list of nodes and edges.
    """
    nodes = []
    edges = []
    
    node_id = tree['person_id']
    nodes.append({
        'id': node_id,
        'label': tree['full_name'],
        'email': tree['email'],
        'job_title': tree['job_title']
    })
    
    if parent:
        edges.append({'source': parent, 'target': node_id})
    
    for child in tree.get('children', []):
        child_nodes, child_edges = parse_tree(child, node_id)
        nodes.extend(child_nodes)
        edges.extend(child_edges)
    
    return nodes, edges