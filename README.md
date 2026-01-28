# Addis Ababa Road Clustering for Smarter Data Collection

This project explores how clustering algorithms—specifically KMeans—can be used to create more meaningful data collection zones in Addis Ababa by analyzing road network proximity, rather than relying on administrative sub-city boundaries.

## Problem Statement

Traditional survey methods often allocate equal samples per administrative sub-city, regardless of their area or population density. This can lead to inefficient or biased data collection.

## Objective

- Cluster roads in Addis Ababa using KMeans based on spatial proximity.
- Identify optimal cluster centers to guide data collection.
- Generate visual and interactive outputs to support field application.

## Tools & Libraries

- **Language**: Python
- **Libraries**: `osmnx`, `geopandas`, `scikit-learn`, `plotly`, `matplotlib`, `seaborn`, `pandas`, `numpy`

## Project Structure

```bash
addis-road-clustering/
├── notebooks/         # Analysis in Jupyter
├── scripts/           # Script version of analysis
├── output/            # Figures and interactive map
├── requirements.txt   # Dependencies
└── README.md
```
## Results

- Road networks grouped into **5 optimal clusters**
- Interactive map showing **cluster centers and road assignments**
- **Silhouette Score** of `0.45` — moderately effective clustering

## Interactive Map

[Click here to view map](./output/map.html)
*Hover to see cluster info; zoom to explore spatial coverage.*

## Limitations

- Clustering only considers **spatial proximity** (no population/income data)
- Only **road centroids** used; not building or service distribution

## Future Work

- Include **population or service access data**
- Use **density-aware clustering** (DBSCAN/HDBSCAN)
- Automate **cluster evaluation and visualization pipeline**

## Related Blog Post

For a detailed walkthrough of the methods, visuals, and reasoning behind this project, check out the blog post on my website:

👉 [Clustering New Addis Ababa 'Sub Cities': A Guide for Data Collectors](https://natnaelgetahun.netlify.app/project/new_subcities/)

## License

MIT License
---

Feel free to **fork**, **modify**, or **build on this work**. If you use or share it, a **credit would be appreciated**!
