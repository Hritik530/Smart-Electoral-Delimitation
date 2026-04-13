class QuadNode:
    def __init__(self, boundary, points):
        self.boundary = boundary # [min_lat, max_lat, min_lon, max_lon]
        self.points = points
        self.children = []
        self.is_leaf = True

def build_quadtree(points, boundary, threshold=1000):
    """
    Recursively splits the geographic area until population < threshold.
    """
    total_pop = points['population'].sum()
    
    if total_pop <= threshold or len(points) <= 1:
        return QuadNode(boundary, points)
    
    node = QuadNode(boundary, points)
    node.is_leaf = False
    
    min_lat, max_lat, min_lon, max_lon = boundary
    mid_lat = (min_lat + max_lat) / 2
    mid_lon = (min_lon + max_lon) / 2
    
    # Define 4 quadrants
    quads = [
        [mid_lat, max_lat, min_lon, mid_lon], # NW
        [mid_lat, max_lat, mid_lon, max_lon], # NE
        [min_lat, mid_lat, min_lon, mid_lon], # SW
        [min_lat, mid_lat, mid_lon, max_lon]  # SE
    ]
    
    for q_bound in quads:
        p_in_q = points[
            (points['latitude'] >= q_bound[0]) & (points['latitude'] < q_bound[1]) &
            (points['longitude'] >= q_bound[2]) & (points['longitude'] < q_bound[3])
        ]
        if not p_in_q.empty:
            node.children.append(build_quadtree(p_in_q, q_bound, threshold))
            
    return node

def get_leaf_nodes(node, leaves=None):
    if leaves is None: leaves = []
    if node.is_leaf:
        leaves.append(node)
    else:
        for child in node.children:
            get_leaf_nodes(child, leaves)
    return leaves