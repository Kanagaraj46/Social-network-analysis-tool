from flask import Flask, render_template, request, redirect, url_for
import networkx as nx
import community as community_louvain
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64
from collections import defaultdict

app = Flask(__name__)

def parse_adjacency_list(content):
    graph = nx.Graph()
    lines = content.split('\n')
    
    for line in lines:
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) < 1:
            continue
        user = parts[0]
        friends = parts[1:]
        for friend in friends:
            graph.add_edge(user, friend)
    
    return graph

def generate_visualization(graph):
    plt.figure(figsize=(12, 8))
    
    # Use spring layout for better visualization
    pos = nx.spring_layout(graph, k=0.3, iterations=50)
    
    # Detect communities for coloring
    partition = community_louvain.best_partition(graph)
    cmap = plt.get_cmap('viridis')
    colors = [partition[node] for node in graph.nodes()]
    
    nx.draw_networkx_nodes(graph, pos, node_size=300, node_color=colors, cmap=cmap, alpha=0.8)
    nx.draw_networkx_edges(graph, pos, width=1.0, alpha=0.5)
    nx.draw_networkx_labels(graph, pos, font_size=8, font_family='sans-serif')
    
    plt.title("Social Network Graph Visualization")
    plt.axis('off')
    
    # Save plot to a bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    plt.close()
    
    # Encode the image to base64 for HTML embedding
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    
    return image_base64

def calculate_metrics(graph):
    if len(graph.nodes()) == 0:
        return {}
    
    metrics = {}
    
    # Centrality measures
    metrics['degree_centrality'] = nx.degree_centrality(graph)
    metrics['betweenness_centrality'] = nx.betweenness_centrality(graph, k=min(100, len(graph.nodes())))
    metrics['closeness_centrality'] = nx.closeness_centrality(graph)
    
    # Community detection
    partition = community_louvain.best_partition(graph)
    metrics['communities'] = partition
    
    # Clustering coefficients for fake account detection
    metrics['clustering_coefficients'] = nx.clustering(graph)
    
    # Average shortest path length
    try:
        metrics['avg_path_length'] = nx.average_shortest_path_length(graph)
    except:
        metrics['avg_path_length'] = "Graph is not connected"
    
    # Density
    metrics['density'] = nx.density(graph)
    
    return metrics

def recommend_friends(graph, user):
    recommendations = {}
    user_neighbors = set(graph.neighbors(user))
    
    for potential_friend in graph.nodes():
        if potential_friend == user or graph.has_edge(user, potential_friend):
            continue
        
        friend_neighbors = set(graph.neighbors(potential_friend))
        common_neighbors = user_neighbors.intersection(friend_neighbors)
        all_neighbors = user_neighbors.union(friend_neighbors)
        
        if len(all_neighbors) > 0:
            jaccard_similarity = len(common_neighbors) / len(all_neighbors)
            recommendations[potential_friend] = jaccard_similarity
    
    return sorted(recommendations.items(), key=lambda x: x[1], reverse=True)[:5]

def detect_potential_fake_accounts(graph, threshold=0.1):
    potential_fakes = []
    clustering_coeffs = nx.clustering(graph)
    avg_clustering = nx.average_clustering(graph)
    
    for node, coeff in clustering_coeffs.items():
        if coeff < threshold * avg_clustering:
            potential_fakes.append((node, coeff))
    
    return sorted(potential_fakes, key=lambda x: x[1])[:10]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        
        if file:
            content = file.read().decode('utf-8')
            graph = parse_adjacency_list(content)
            
            if len(graph.nodes()) == 0:
                return render_template('index.html', error="No valid data found in the file.")
            
            # Generate visualization
            visualization = generate_visualization(graph)
            
            # Calculate metrics
            metrics = calculate_metrics(graph)
            
            # Get top influencers
            top_degree = sorted(metrics['degree_centrality'].items(), key=lambda x: x[1], reverse=True)[:5]
            top_betweenness = sorted(metrics['betweenness_centrality'].items(), key=lambda x: x[1], reverse=True)[:5]
            top_closeness = sorted(metrics['closeness_centrality'].items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Community statistics
            community_stats = defaultdict(int)
            for node, comm in metrics['communities'].items():
                community_stats[comm] += 1
            
            # Friend recommendations for a random user or the most central user
            sample_user = top_degree[0][0] if top_degree else list(graph.nodes())[0]
            recommendations = recommend_friends(graph, sample_user)
            
            # Fake account detection
            potential_fakes = detect_potential_fake_accounts(graph)
            
            return render_template('results.html',
                                 visualization=visualization,
                                 num_nodes=len(graph.nodes()),
                                 num_edges=len(graph.edges()),
                                 density=metrics['density'],
                                 avg_path_length=metrics['avg_path_length'],
                                 top_degree=top_degree,
                                 top_betweenness=top_betweenness,
                                 top_closeness=top_closeness,
                                 community_stats=dict(community_stats),
                                 sample_user=sample_user,
                                 recommendations=recommendations,
                                 potential_fakes=potential_fakes)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)