# Social Network Analysis Tool

A web-based tool for analyzing social networks using graph theory algorithms.

## Features

- Network visualization
- Community detection (Louvain algorithm)
- Influencer identification (centrality measures)
- Friend recommendations (Jaccard similarity)
- Fake account detection (clustering coefficient)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/sna-tool.git
   cd sna-tool
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the Flask application:
   ```bash
   python app.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

3. Upload an adjacency list file with the following format:
   ```
   user1 user2 user3
   user2 user1 user4
   user3 user1
   user4 user2
   ```

## Sample Data

A sample input file `sample_network.txt` is provided in the repository.

## Project Structure

```
sna-tool/
├── app.py                  # Flask backend (Graph analysis logic)
├── static/
│   └── styles.css          # CSS for styling
├── templates/
│   ├── index.html          # Input form (upload adjacency list)
│   └── results.html        # Visualization + analysis results
├── requirements.txt        # Dependencies
└── README.md               # Setup instructions
```

## License

MIT