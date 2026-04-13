from sklearn.cluster import AgglomerativeClustering
import numpy as np

def group_into_constituencies(leaf_data, n_clusters=5):
    """
    Groups quadtree leaf cells into larger constituencies using Spatial Clustering.
    """
    # Features: Centroid of cell and average socio-economic score
    features = leaf_data[['avg_lat', 'avg_lon', 'avg_socio']].values
    
    clustering = AgglomerativeClustering(n_clusters=n_clusters)
    labels = clustering.fit_predict(features)
    
    return labels