# ShortPath - Graph Shortest Path System

A complete system for calculating and visualizing shortest paths in graphs, consisting of a REST API, core graph algorithms, and interactive web interface.

<p align="center">
  <img src="/assets/image.png" height="440">
</p>


## Architecture

- **REST API** (Python/FastAPI) - Core shortest path calculations
- **Web UI** (React/TypeScript) - Interactive graph visualization  
- **Redis Storage** - In-memory graph storage with TTL
- **Docker Compose** - Development and deployment environment

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ and Poetry (for local development)
- Node.js 18+ (for local development)

### Development Setup

1. **Clone and start services**:
   ```bash
   git clone <repository-url>
   cd shortest-path
   docker-compose up -d
   ```

2. **Access services**:
   - API: http://localhost:8000
   - Web UI: http://localhost:3000
   - API Docs: http://localhost:8000/docs
   - Redis: localhost:6379

### Local Development

#### API Development
```bash
cd api
poetry install
poetry run uvicorn app.main:app --reload
```

#### UI Development
```bash
cd ui
npm install
npm start
```

### Testing the API

```bash
# Create a graph
curl -X POST http://localhost:8000/graphs \
  -H "Content-Type: application/json" \
  -d '{
    "directed": false,
    "nodes": ["A", "B", "C"],
    "edges": [
      {"from": "A", "to": "B", "weight": 5},
      {"from": "B", "to": "C", "weight": 3}
    ]
  }'

# Calculate shortest path (use returned graph_id)
curl -X POST http://localhost:8000/graphs/{graph_id}/shortest-path \
  -H "Content-Type: application/json" \
  -d '{
    "source": "A",
    "target": "C",
    "algorithm": "dijkstra"
  }'
```

## Features

### Core Functionality
- ✅ Dijkstra algorithm for weighted graphs
- ✅ BFS algorithm for unweighted graphs  
- ✅ A* algorithm with Euclidean heuristic
- ✅ Graph validation and error handling
- ✅ 24-hour automatic graph expiration

### Performance
- Supports graphs up to 10,000 nodes
- Path calculation: <5 seconds for 1,000 nodes
- Visualization: <30 seconds for 10,000 nodes
- Concurrent requests: 100 simultaneous without degradation

### Web Interface
- Interactive graph visualization with D3.js
- Drag-and-drop graph upload
- Real-time path highlighting
- Algorithm performance comparison

## API Documentation

Visit http://localhost:8000/docs for interactive API documentation.

## Project Structure

```
shortest-path/
├── api/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py        # FastAPI application
│   │   ├── models/        # Pydantic models
│   │   ├── routers/       # API endpoints
│   │   ├── services/      # Business logic
│   │   └── algorithms/    # Graph algorithms
│   ├── tests/             # Backend tests
│   └── pyproject.toml     # Python dependencies
├── ui/                     # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── services/      # API client
│   │   └── utils/         # Utility functions
│   └── package.json       # Node.js dependencies
├── docker-compose.yml      # Development environment
└── README.md
```
