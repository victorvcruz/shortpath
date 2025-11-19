import React, { useState, useEffect } from 'react';
import { PathQuery, PathResult, AlgorithmRecommendation } from '../types/graph';

interface PathFinderProps {
  graphId: string | null;
  availableNodes?: string[];
  onPathCalculate: (query: PathQuery) => void;
  pathResult: PathResult | null;
  loading?: boolean;
  recommendations?: AlgorithmRecommendation | null;
}

const PathFinder: React.FC<PathFinderProps> = ({
  graphId,
  availableNodes = [],
  onPathCalculate,
  pathResult,
  loading,
  recommendations
}) => {
  const [source, setSource] = useState<string>('');
  const [target, setTarget] = useState<string>('');
  const [algorithm, setAlgorithm] = useState<'dijkstra' | 'bfs' | 'astar'>('dijkstra');

  useEffect(() => {
    if (availableNodes && availableNodes.length >= 2 && !source && !target) {
      setSource(availableNodes[0]);
      setTarget(availableNodes[1]);
    }
  }, [availableNodes, source, target]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!source || !target) return;

    const query: PathQuery = {
      source,
      target,
      algorithm
    };

    onPathCalculate(query);
  };

  const canCalculate = source && target && source !== target && !loading;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-slate-900 mb-4">Find Shortest Path</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Source Node */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Source Node
            </label>
            <select
              value={source}
              onChange={(e) => setSource(e.target.value)}
              className="input-field"
              required
            >
              <option value="">Select source node</option>
              {availableNodes && availableNodes.map(node => (
                <option key={node} value={node}>{node}</option>
              ))}
            </select>
          </div>

          {/* Target Node */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Target Node
            </label>
            <select
              value={target}
              onChange={(e) => setTarget(e.target.value)}
              className="input-field"
              required
            >
              <option value="">Select target node</option>
              {availableNodes && availableNodes.map(node => (
                <option key={node} value={node}>{node}</option>
              ))}
            </select>
          </div>

          {/* Algorithm Selection */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Algorithm
            </label>
            <div className="space-y-2">
              <label className="flex items-center space-x-3">
                <input
                  type="radio"
                  name="algorithm"
                  value="dijkstra"
                  checked={algorithm === 'dijkstra'}
                  onChange={(e) => setAlgorithm(e.target.value as any)}
                  className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500 focus:ring-2"
                />
                <div>
                  <span className="text-sm font-medium text-slate-700">Dijkstra</span>
                  <p className="text-xs text-slate-500">Optimal for weighted graphs</p>
                </div>
              </label>
              <label className="flex items-center space-x-3">
                <input
                  type="radio"
                  name="algorithm"
                  value="bfs"
                  checked={algorithm === 'bfs'}
                  onChange={(e) => setAlgorithm(e.target.value as any)}
                  className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500 focus:ring-2"
                />
                <div>
                  <span className="text-sm font-medium text-slate-700">BFS</span>
                  <p className="text-xs text-slate-500">Best for unweighted graphs</p>
                </div>
              </label>
              <label className="flex items-center space-x-3">
                <input
                  type="radio"
                  name="algorithm"
                  value="astar"
                  checked={algorithm === 'astar'}
                  onChange={(e) => setAlgorithm(e.target.value as any)}
                  className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500 focus:ring-2"
                />
                <div>
                  <span className="text-sm font-medium text-slate-700">A*</span>
                  <p className="text-xs text-slate-500">Heuristic-based pathfinding</p>
                </div>
              </label>
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={!canCalculate}
            className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <div className="flex items-center justify-center space-x-2">
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>Finding Path...</span>
              </div>
            ) : (
              'Find Path'
            )}
          </button>
        </form>

        {/* Path Result */}
        {pathResult && (
          <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
            <h3 className="text-sm font-semibold text-green-800 mb-2">Path Found!</h3>
            <div className="space-y-2 text-sm">
              <div>
                <span className="text-green-700 font-medium">Path:</span>
                <span className="ml-2 font-mono text-green-800">
                  {pathResult.path.join(' → ')}
                </span>
              </div>
              <div>
                <span className="text-green-700 font-medium">Distance:</span>
                <span className="ml-2 font-mono text-green-800">
                  {pathResult.distance.toFixed(2)}
                </span>
              </div>
              <div>
                <span className="text-green-700 font-medium">Algorithm:</span>
                <span className="ml-2 text-green-800 capitalize">
                  {pathResult.algorithm_used}
                </span>
              </div>
              {pathResult.execution_time_ms && (
                <div>
                  <span className="text-green-700 font-medium">Time:</span>
                  <span className="ml-2 text-green-800">
                    {pathResult.execution_time_ms.toFixed(2)}ms
                  </span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Recommendations */}
        {recommendations && (
          <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h3 className="text-sm font-semibold text-blue-800 mb-2">Algorithm Recommendations</h3>
            <div className="space-y-2 text-sm">
              <div>
                <span className="text-blue-700 font-medium">Recommended:</span>
                <span className="ml-2 text-blue-800 capitalize">
                  {recommendations.primary}
                </span>
              </div>
              <div>
                <span className="text-blue-700 font-medium">Reason:</span>
                <span className="ml-2 text-blue-800">
                  {recommendations.reasoning.join(', ')}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PathFinder;