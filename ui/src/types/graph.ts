export interface Node {
  id: string;
  label?: string;
  x?: number;
  y?: number;
  fx?: number | null;
  fy?: number | null;
  properties?: Record<string, any>;
}

export interface Edge {
  source: string | Node;
  target: string | Node;
  from?: string;
  to?: string;
  from_node?: string;
  to_node?: string;
  weight: number;
  properties?: Record<string, any>;
}

export interface GraphMetadata {
  node_count: number;
  edge_count: number;
  is_connected: boolean;
  has_cycles: boolean;
  density: number;
  components: number;
}

export interface Graph {
  id?: string;
  directed: boolean;
  nodes: string[];
  edges: Array<{
    from_node: string;
    to_node: string;
    weight: number;
    properties?: Record<string, any>;
  }>;
  created_at?: string;
  last_accessed?: string;
  metadata?: GraphMetadata;
}

export interface GraphInput {
  directed: boolean;
  nodes: string[];
  edges: Array<{
    from: string;
    to: string;
    weight: number;
  }>;
}

export interface GraphResponse {
  graph_id: string;
  created_at: string;
  metadata: GraphMetadata;
}

export interface PathQuery {
  source: string;
  target: string;
  algorithm: 'dijkstra' | 'bfs' | 'astar';
  include_visited?: boolean;
}

export interface PathResult {
  path: string[];
  distance: number;
  algorithm_used: string;
  execution_time_ms: number;
  visited_nodes_count: number;
  visited_nodes?: string[] | null;
  exists: boolean;
}

export interface AlgorithmRecommendation {
  primary: string;
  alternatives: string[];
  reasoning: string[];
  graph_stats: {
    nodes: number;
    edges: number;
    directed: boolean;
    density: number;
  };
}

