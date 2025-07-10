#importing needed libraries
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns

import osmnx as ox

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

import plotly.express as px
import plotly.graph_objects as go

# Define location and tags
place = "አዲስ አበባ Addis Ababa أديس أبابا, ኢትዮጵያ إثيوبيا"
tags = {"boundary": "administrative", "admin_level": "30"}

# Load subcities as polygons
gdf = ox.features_from_place(place, tags)
gdf = gdf[gdf.geometry.type.isin(["Polygon", "MultiPolygon"])]
gdf.plot(figsize=(8, 8), edgecolor="black", color="lightblue")
plt.show()

#filtering only sub cities of Addis Ababa (no Lemi Kura in openstreetmap's data)
gdf_filtered = gdf.loc[gdf["name"].isin([
    'Arada', 'Bole', 'Addis Ketema',
    'Kirkos', 'Gulale', 'Lideta', 'Yeka',
    'Nefas Silk', 'Akaki Kaliti', 'Kolfe Keranio'
]), ["name", "geometry"]].reset_index(drop=True)

# Plot with color and figsize
gdf_filtered.plot(edgecolor="black", color="lightgreen", figsize=(8, 8));
plt.show()

#getting shop features
place = "Addis Ababa, Ethiopia"
tags = {"shop": True}
poi = ox.features_from_place("Addis Ababa, Ethiopia", tags)

#getting building features
tags = {"building" : True}
buildings = ox.features_from_place(place, tags)
buildings = buildings[buildings.geometry.type.isin(["Polygon", "MultiPolygon"])]

#getting road networks
G = ox.graph_from_place(place, network_type="drive")
edges = ox.graph_to_gdfs(G, nodes=False)

#plotting shop, buildings, and roads to see which features come close to showing population density
fig, ax = plt.subplots(1, 1, figsize=(10, 10))

edges.plot(ax=ax, edgecolor="red", linewidth=0.5, alpha=0.5)
buildings.plot(ax=ax, edgecolor="green", alpha=0.3)
gdf_filtered.plot(ax=ax, edgecolor="black", cmap="Pastel2", alpha=0.5)
poi.plot(ax=ax, markersize=8, color="blue", zorder=3)

plt.show()

#taking the roads line column only
edges = edges[["geometry"]].reset_index(drop=True)
edges.head()

#checking the crs
edges.crs

edge_points = edges.copy()
#converting to meters crs (UTM zone 37N for Ethiopia)
edge_points = edge_points.to_crs("EPSG:32637")
edge_points.crs

# calculating the mid point of the road
# .centroid can pick a point outside the road for curved roads
# normalized=True means 0.5 refers to 50% of the line's length not absolute distance
edge_points["geometry"] = edge_points.geometry.interpolate(0.5, normalized=True)
edge_points["x"] = edge_points.geometry.x
edge_points["y"] = edge_points.geometry.y
edge_points.head()

# convering to numpy array and scaling
X = edge_points[["x", "y"]].values
scaler = StandardScaler()
X = scaler.fit_transform(X)

# plotting an elbow plot
distortions = []
K = range(1, 20)
for k in K:
    kmeans = KMeans(n_clusters=k)
    kmeans.fit(X)
    distortions.append(kmeans.inertia_)
plt.figure(figsize=(16, 10))
plt.plot(K, distortions, "bx-")
plt.title("Elbow Method for optimal K")
plt.xlabel("k")
plt.ylabel("Distortion")
plt.show()

# building and fitting KMeans clustering
kmeans = KMeans(n_clusters=5, random_state=42)
kmeans_7 = kmeans.fit(X)
kmeans_7.labels_

# creating a column with the clusters
edge_points["cluster"] = kmeans_7.labels_
edge_points = edge_points.set_geometry("geometry")

# converting to degrees
edge_points_latlon = edge_points.to_crs("EPSG:4326")

#Kmeans plot
fig, ax = plt.subplots(figsize=(10, 10))
edge_points_latlon.plot(column="cluster", ax=ax, cmap="tab20", markersize=50)
gdf_filtered.plot(edgecolor="grey", ax=ax, facecolor="none", linewidth=1)
plt.title("Road Clusters by Density and Proximity")
ax.set_axis_off()
plt.show()

#Extracting cluster centroids
cluster_centers = scaler.inverse_transform(kmeans.cluster_centers_)
cluster_centers_gdf = gpd.GeoDataFrame(geometry=gpd.points_from_xy(cluster_centers[:, 0], cluster_centers[:, 1]), crs="EPSG:32637")
cluster_centers_gdf = cluster_centers_gdf.to_crs("EPSG:4326")
cluster_coords = cluster_centers_gdf.geometry.apply(lambda pt: (pt.y, pt.x))

cluster_coords

#evaluating the model
score = silhouette_score(X, edge_points["cluster"])
print(f"Silhouette Score: {score:.2f}")

# Convert clusters to DataFrame
cluster_df = pd.DataFrame({
    'lat': edge_points_latlon.geometry.y,
    'lon': edge_points_latlon.geometry.x,
    'cluster': edge_points_latlon['cluster'] + 1  # Clusters start from 1
})

# Create base scatter map
fig = px.scatter_map(
    cluster_df,
    lat="lat",
    lon="lon",
    color="cluster",
    color_discrete_sequence=px.colors.qualitative.Plotly,
    zoom=11,
    height=800,
    title="Addis Ababa Road Clusters",
    opacity=0.3,
    hover_data=['cluster'],
    map_style="open-street-map"
)

# Add cluster centers with prominent markers
centroid_df = pd.DataFrame({
    'lat': [pt.y for pt in cluster_centers_gdf.geometry],
    'lon': [pt.x for pt in cluster_centers_gdf.geometry],
    'cluster': [f"Cluster Center {i+1}" for i in range(len(cluster_centers_gdf))]
})


fig.add_trace(go.Scattermap(
    lat=centroid_df['lat'],
    lon=centroid_df['lon'],
    mode='markers+text',
    marker=dict(
        size=24,  # Larger size
        color='darkorange',  # Vibrant color
        symbol='triangle-up',  # Distinct shape
        opacity=1
    ),
    text=centroid_df['cluster'],
    textposition="top center",
    textfont=dict(
        size=30,
        color='white'
    ),
    hoverinfo='text',
    name='Cluster Centers'
))

# Configure map view
fig.update_layout(
    mapbox=dict(
        center=dict(lat=9.03, lon=38.74),
        zoom=11,
    ),
    margin={"r":0,"t":40,"l":0,"b":0},
    showlegend=True,
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    )
)

# Style regular points
fig.update_traces(
    marker=dict(
        size=4,
        opacity=0.3
    ),
    selector=dict(mode='markers')
)

fig.write_html("output/map.html")