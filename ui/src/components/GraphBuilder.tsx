import React, { useState } from 'react';
import { GraphInput } from '../types/graph';

interface GraphBuilderProps {
  onGraphCreate: (graph: GraphInput) => void;
  loading?: boolean;
}

const GraphBuilder: React.FC<GraphBuilderProps> = ({ onGraphCreate, loading }) => {
  const [directed, setDirected] = useState(false);
  const [nodes, setNodes] = useState<string>('A,B,C,D');
  const [edges, setEdges] = useState<string>('A,B,5\nB,C,3\nC,D,2\nA,D,8');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const nodeList = nodes.split(',').map(n => n.trim()).filter(n => n);
      
      const edgeList = edges.split('\n')
        .map(line => line.trim())
        .filter(line => line)
        .map(line => {
          const parts = line.split(',').map(p => p.trim());
          if (parts.length !== 3) {
            throw new Error(`Invalid edge format: ${line}. Expected: from,to,weight`);
          }
          return {
            from: parts[0],
            to: parts[1],
            weight: parseFloat(parts[2])
          };
        });

      if (nodeList.length === 0) {
        throw new Error('At least one node is required');
      }

      const nodeSet = new Set(nodeList);
      for (const edge of edgeList) {
        if (!nodeSet.has(edge.from)) {
          throw new Error(`Edge references non-existent node: ${edge.from}`);
        }
        if (!nodeSet.has(edge.to)) {
          throw new Error(`Edge references non-existent node: ${edge.to}`);
        }
        if (isNaN(edge.weight) || edge.weight <= 0) {
          throw new Error(`Invalid weight for edge ${edge.from}-${edge.to}: ${edge.weight}`);
        }
      }

      const graphInput: GraphInput = {
        directed,
        nodes: nodeList,
        edges: edgeList
      };

      onGraphCreate(graphInput);
    } catch (error: any) {
      alert(error.message);
    }
  };

  const loadSampleGraph = (type: 'simple' | 'complex' | 'tree' | 'cycle') => {
    switch (type) {
      case 'simple':
        setNodes('A,B,C');
        setEdges('A,B,1\nB,C,1');
        setDirected(false);
        break;
      case 'complex':
        setNodes('A,B,C,D,E,F');
        setEdges('A,B,4\nA,C,2\nB,C,1\nB,D,5\nC,D,8\nC,E,10\nD,E,2\nD,F,6\nE,F,3');
        setDirected(false);
        break;
      case 'tree':
        setNodes('Root,A,B,C,D,E');
        setEdges('Root,A,1\nRoot,B,1\nA,C,2\nA,D,3\nB,E,2');
        setDirected(true);
        break;
      case 'cycle':
        setNodes('A,B,C,D');
        setEdges('A,B,1\nB,C,2\nC,D,1\nD,A,3');
        setDirected(true);
        break;
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-slate-900 mb-4">Create Graph</h2>
        
        {/* Sample Graphs */}
        <div className="mb-6">
          <h3 className="text-sm font-medium text-slate-700 mb-3">Quick Start</h3>
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={() => loadSampleGraph('simple')}
              className="text-xs bg-blue-50 hover:bg-blue-100 text-blue-700 px-3 py-2 rounded-lg border border-blue-200 transition-colors"
            >
              Simple Path
            </button>
            <button
              onClick={() => loadSampleGraph('complex')}
              className="text-xs bg-purple-50 hover:bg-purple-100 text-purple-700 px-3 py-2 rounded-lg border border-purple-200 transition-colors"
            >
              Complex Graph
            </button>
            <button
              onClick={() => loadSampleGraph('tree')}
              className="text-xs bg-green-50 hover:bg-green-100 text-green-700 px-3 py-2 rounded-lg border border-green-200 transition-colors"
            >
              Tree Structure
            </button>
            <button
              onClick={() => loadSampleGraph('cycle')}
              className="text-xs bg-orange-50 hover:bg-orange-100 text-orange-700 px-3 py-2 rounded-lg border border-orange-200 transition-colors"
            >
              With Cycles
            </button>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Graph Type */}
          <div>
            <label className="flex items-center space-x-3">
              <input
                type="checkbox"
                checked={directed}
                onChange={(e) => setDirected(e.target.checked)}
                className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2"
              />
              <span className="text-sm font-medium text-slate-700">Directed Graph</span>
            </label>
          </div>

          {/* Nodes Input */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Nodes (comma-separated)
            </label>
            <input
              type="text"
              value={nodes}
              onChange={(e) => setNodes(e.target.value)}
              className="input-field"
              placeholder="A,B,C,D"
              required
            />
            <p className="mt-1 text-xs text-slate-500">
              Enter node names separated by commas
            </p>
          </div>

          {/* Edges Input */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Edges (one per line: from,to,weight)
            </label>
            <textarea
              value={edges}
              onChange={(e) => setEdges(e.target.value)}
              className="input-field min-h-[120px] font-mono text-sm"
              placeholder="A,B,5&#10;B,C,3&#10;C,D,2"
              required
            />
            <p className="mt-1 text-xs text-slate-500">
              Format: source,target,weight (one edge per line)
            </p>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <div className="flex items-center justify-center space-x-2">
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>Creating Graph...</span>
              </div>
            ) : (
              'Create Graph'
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default GraphBuilder;