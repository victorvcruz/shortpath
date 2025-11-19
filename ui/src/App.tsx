import React, { useState, useEffect } from 'react';
import GraphBuilder from './components/GraphBuilder';
import GraphVisualization from './components/GraphVisualization';
import PathFinder from './components/PathFinder';
import apiService from './services/api';
import {
    Graph,
    GraphInput,
    GraphResponse,
    PathQuery,
    PathResult,
    AlgorithmRecommendation
} from './types/graph';

function App() {
    const [graph, setGraph] = useState<Graph | null>(null);
    const [graphId, setGraphId] = useState<string | null>(null);
    const [pathResult, setPathResult] = useState<PathResult | null>(null);
    const [recommendations, setRecommendations] = useState<AlgorithmRecommendation | null>(null);
    const [selectedNodes, setSelectedNodes] = useState<{ source?: string; target?: string }>({});
    const [loading, setLoading] = useState({
        createGraph: false,
        calculatePath: false,
        loadRecommendations: false
    });
    const [error, setError] = useState<string | null>(null);
    const [apiStatus, setApiStatus] = useState<'checking' | 'online' | 'offline'>('checking');

    useEffect(() => {
        checkApiStatus();
    }, []);

    const checkApiStatus = async () => {
        try {
            const isOnline = await apiService.ping();
            setApiStatus(isOnline ? 'online' : 'offline');
        } catch {
            setApiStatus('offline');
        }
    };

    const handleGraphCreate = async (graphInput: GraphInput) => {
        setLoading(prev => ({ ...prev, createGraph: true }));
        setError(null);

        try {
            const response: GraphResponse = await apiService.createGraph(graphInput);
            const fullGraph = await apiService.getGraph(response.graph_id);

            setGraph(fullGraph);
            setGraphId(response.graph_id);
            setPathResult(null);
            setRecommendations(null);

            if (fullGraph.nodes && fullGraph.nodes.length >= 2) {
                setSelectedNodes({
                    source: fullGraph.nodes[0],
                    target: fullGraph.nodes[1]
                });
            }

        } catch (err: any) {
            setError(err.message || 'Failed to create graph');
        } finally {
            setLoading(prev => ({ ...prev, createGraph: false }));
        }
    };

    const handlePathCalculate = async (pathQuery: PathQuery) => {
        if (!graphId) return;

        setLoading(prev => ({ ...prev, calculatePath: true }));
        setError(null);

        try {
            const result = await apiService.calculateShortestPath(graphId, pathQuery);
            setPathResult(result);

            setLoading(prev => ({ ...prev, loadRecommendations: true }));
            try {
                const recs = await apiService.getAlgorithmRecommendations(graphId);
                setRecommendations(recs);
            } catch (recError) {
                console.warn('Failed to load recommendations:', recError);
            }

        } catch (err: any) {
            setError(err.message || 'Failed to calculate path');
        } finally {
            setLoading(prev => ({
                ...prev,
                calculatePath: false,
                loadRecommendations: false
            }));
        }
    };

    const handleNodeClick = (nodeId: string) => {
        if (!selectedNodes.source) {
            setSelectedNodes({ source: nodeId });
        } else if (!selectedNodes.target && nodeId !== selectedNodes.source) {
            setSelectedNodes(prev => ({ ...prev, target: nodeId }));
        } else {
            setSelectedNodes({ source: nodeId });
        }
    };

    const clearGraph = () => {
        setGraph(null);
        setGraphId(null);
        setPathResult(null);
        setRecommendations(null);
        setSelectedNodes({});
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
            {/* Header */}
            <header className="bg-white/80 backdrop-blur-sm border-b border-slate-200 sticky top-0 z-50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-center h-16">
                        <div className="flex items-center space-x-4">
                            <div className="flex items-center space-x-3">
                                <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                                    </svg>
                                </div>
                                <div>
                                    <h1 className="text-xl font-bold text-slate-900">ShortPath</h1>
                                    <p className="text-sm text-slate-600">Interactive Graph Pathfinding</p>
                                </div>
                            </div>
                        </div>

                        <div className="flex items-center space-x-4">
                            <div className={`flex items-center space-x-2 px-3 py-1.5 rounded-full text-sm font-medium ${apiStatus === 'online' ? 'bg-green-100 text-green-800' :
                                    apiStatus === 'offline' ? 'bg-red-100 text-red-800' :
                                        'bg-yellow-100 text-yellow-800'
                                }`}>
                                <div className={`w-2 h-2 rounded-full ${apiStatus === 'online' ? 'bg-green-500' :
                                        apiStatus === 'offline' ? 'bg-red-500' :
                                            'bg-yellow-500 animate-pulse'
                                    }`}></div>
                                <span>API {apiStatus === 'checking' ? 'Checking...' : apiStatus}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </header>

            {/* Error Banner */}
            {error && (
                <div className="bg-red-50 border-l-4 border-red-400 p-4 animate-slide-up">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center">
                            <div className="flex-shrink-0">
                                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                                </svg>
                            </div>
                            <div className="ml-3">
                                <p className="text-sm text-red-700">{error}</p>
                            </div>
                        </div>
                        <button
                            onClick={() => setError(null)}
                            className="text-red-400 hover:text-red-600 transition-colors"
                        >
                            <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                            </svg>
                        </button>
                    </div>
                </div>
            )}

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Sidebar */}
                    <div className="lg:col-span-1 space-y-6">
                        <div className="card animate-fade-in">
                            <GraphBuilder
                                onGraphCreate={handleGraphCreate}
                                loading={loading.createGraph}
                            />
                        </div>

                        {graph && (
                            <div className="card animate-slide-up">
                                <PathFinder
                                    graphId={graphId}
                                    availableNodes={graph.nodes || []}
                                    onPathCalculate={handlePathCalculate}
                                    pathResult={pathResult}
                                    loading={loading.calculatePath}
                                    recommendations={recommendations}
                                />
                            </div>
                        )}

                        {graph && (
                            <div className="card animate-slide-up">
                                <div className="flex items-center justify-between mb-4">
                                    <h3 className="text-lg font-semibold text-slate-900">Graph Information</h3>
                                    <button
                                        onClick={clearGraph}
                                        className="text-red-600 hover:text-red-700 text-sm font-medium"
                                    >
                                        Clear Graph
                                    </button>
                                </div>

                                <div className="grid grid-cols-2 gap-3 text-sm">
                                    <div className="bg-slate-50 p-3 rounded-lg">
                                        <div className="text-slate-600">Type</div>
                                        <div className="font-semibold text-slate-900">
                                            {graph.directed ? 'Directed' : 'Undirected'}
                                        </div>
                                    </div>
                                    <div className="bg-slate-50 p-3 rounded-lg">
                                        <div className="text-slate-600">Nodes</div>
                                        <div className="font-semibold text-slate-900">
                                            {graph.metadata?.node_count || graph.nodes.length}
                                        </div>
                                    </div>
                                    <div className="bg-slate-50 p-3 rounded-lg">
                                        <div className="text-slate-600">Edges</div>
                                        <div className="font-semibold text-slate-900">
                                            {graph.metadata?.edge_count || graph.edges.length}
                                        </div>
                                    </div>
                                    <div className="bg-slate-50 p-3 rounded-lg">
                                        <div className="text-slate-600">Connected</div>
                                        <div className="font-semibold text-slate-900">
                                            {graph.metadata?.is_connected ? 'Yes' : 'No'}
                                        </div>
                                    </div>
                                    <div className="bg-slate-50 p-3 rounded-lg">
                                        <div className="text-slate-600">Cycles</div>
                                        <div className="font-semibold text-slate-900">
                                            {graph.metadata?.has_cycles ? 'Yes' : 'No'}
                                        </div>
                                    </div>
                                    <div className="bg-slate-50 p-3 rounded-lg">
                                        <div className="text-slate-600">Density</div>
                                        <div className="font-semibold text-slate-900">
                                            {(graph.metadata?.density || 0).toFixed(3)}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Visualization Area */}
                    <div className="lg:col-span-2">
                        <div className="card h-full min-h-[600px] animate-fade-in">
                            {graph ? (
                                <div className="h-full">
                                    <div className="flex items-center justify-between mb-4">
                                        <h3 className="text-lg font-semibold text-slate-900">Graph Visualization</h3>
                                        <div className="flex items-center space-x-2 text-sm text-slate-600">
                                            <span>{graph.nodes?.length || 0} nodes</span>
                                            <span>•</span>
                                            <span>{graph.edges?.length || 0} edges</span>
                                        </div>
                                    </div>
                                    <GraphVisualization
                                        graph={graph}
                                        path={pathResult}
                                        onNodeClick={handleNodeClick}
                                        selectedNodes={selectedNodes}
                                        width={800}
                                        height={500}
                                    />
                                </div>
                            ) : (
                                <div className="flex flex-col items-center justify-center h-full text-center py-12">
                                    <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mb-4">
                                        <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                                        </svg>
                                    </div>
                                    <h3 className="text-xl font-semibold text-slate-900 mb-2">No Graph Loaded</h3>
                                    <p className="text-slate-600 mb-6 max-w-md">Create a graph using the form on the left to see the interactive visualization.</p>

                                    <div className="bg-slate-50 rounded-lg p-6 max-w-sm">
                                        <h4 className="font-semibold text-slate-900 mb-3">Quick Start:</h4>
                                        <ol className="text-sm text-slate-600 space-y-2 text-left">
                                            <li className="flex items-start space-x-2">
                                                <span className="flex-shrink-0 w-5 h-5 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-semibold">1</span>
                                                <span>Click a sample graph button</span>
                                            </li>
                                            <li className="flex items-start space-x-2">
                                                <span className="flex-shrink-0 w-5 h-5 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-semibold">2</span>
                                                <span>Click "Create Graph"</span>
                                            </li>
                                            <li className="flex items-start space-x-2">
                                                <span className="flex-shrink-0 w-5 h-5 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-semibold">3</span>
                                                <span>Select source and target nodes</span>
                                            </li>
                                            <li className="flex items-start space-x-2">
                                                <span className="flex-shrink-0 w-5 h-5 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-semibold">4</span>
                                                <span>Click "Find Path"</span>
                                            </li>
                                        </ol>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </main>

            {/* Footer */}
            <footer>
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                    <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
                        <div className="flex items-center space-x-4 text-sm text-slate-600">
                        </div>
                        <div className="flex items-center space-x-4 text-sm text-slate-600">
                            <span>
                                Built by{" "}
                                <a
                                    href="https://github.com/victorvcruz"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-blue-600 hover:underline"
                                >
                                    @victorvcruz
                                </a> see the code on <a href="https://github.com/victorvcruz/shortpath" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">GitHub</a>
                            </span>
                        </div>
                    </div>
                </div>
            </footer>
        </div>
    );
}

export default App;