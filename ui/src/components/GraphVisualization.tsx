import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { Graph, Node, Edge, PathResult } from '../types/graph';

interface GraphVisualizationProps {
  graph: Graph | null;
  path?: PathResult | null;
  onNodeClick?: (nodeId: string) => void;
  selectedNodes?: { source?: string; target?: string };
  width?: number;
  height?: number;
}

const GraphVisualization: React.FC<GraphVisualizationProps> = ({
  graph,
  path,
  onNodeClick,
  selectedNodes,
  width = 800,
  height = 600
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const simulationRef = useRef<d3.Simulation<Node, Edge> | null>(null);

  useEffect(() => {
    if (!graph || !graph.nodes || !graph.edges || !svgRef.current) return;
    if (graph.nodes.length === 0) return;
    
    if (!Array.isArray(graph.nodes) || !Array.isArray(graph.edges)) {
      console.error('Invalid graph data: nodes and edges must be arrays');
      return;
    }

    // Stop previous simulation
    if (simulationRef.current) {
      simulationRef.current.stop();
    }

    d3.select(svgRef.current).selectAll('*').remove();

    const svg = d3.select(svgRef.current);
    const g = svg.append('g');

    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.5, 2])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
      });

    const initialTransform = d3.zoomIdentity.translate(0, 0).scale(1);
    svg.call(zoom.transform, initialTransform);

    svg.call(zoom);

    // Reset zoom to initial state
    const resetZoom = () => {
      const initialTransform = d3.zoomIdentity.translate(0, 0).scale(1);
      svg.transition().duration(500).call(zoom.transform, initialTransform);
    };

    // Reset zoom when new graph is loaded
    resetZoom();

    const nodes: Node[] = (graph?.nodes || []).map((nodeId, index) => {
      const angle = (index / graph.nodes.length) * 2 * Math.PI;
      const baseRadius = Math.min(width, height) * 0.25;
      const radius = Math.max(baseRadius, 80); // Minimum radius of 80px
      return {
        id: nodeId,
        x: width / 2 + Math.cos(angle) * radius,
        y: height / 2 + Math.sin(angle) * radius
      };
    });

    const validEdges = (graph?.edges || []).filter(edge => 
      graph.nodes.includes(edge.from_node) && graph.nodes.includes(edge.to_node)
    );

    const edges: Edge[] = validEdges.map(edge => ({
      source: edge.from_node,
      target: edge.to_node,
      weight: edge.weight
    }));

    const sim = d3.forceSimulation<Node>(nodes)
      .force('link', d3.forceLink<Node, Edge>(edges)
        .id(d => d.id)
        .distance(Math.min(width, height) * 0.2)
        .strength(0.4)
      )
      .force('charge', d3.forceManyBody().strength(-400))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(35))
      .force('x', d3.forceX(width / 2).strength(0.05))
      .force('y', d3.forceY(height / 2).strength(0.05))
      .alpha(0.5)
      .alphaDecay(0.03);

    if (nodes.length === 0) {
      console.warn('No nodes to simulate');
      return;
    }

  // store simulation in ref to avoid triggering re-renders
  simulationRef.current = sim;

    const link = g.append('g')
      .attr('class', 'links')
      .selectAll('line')
      .data(edges)
      .enter()
      .append('line')
      .attr('class', 'edge')
      .style('stroke', d => {
        if (path && path.path.length > 1) {
          for (let i = 0; i < path.path.length - 1; i++) {
            const sourceId = typeof d.source === 'string' ? d.source : d.source.id;
            const targetId = typeof d.target === 'string' ? d.target : d.target.id;
            if ((sourceId === path.path[i] && targetId === path.path[i + 1]) ||
                (sourceId === path.path[i + 1] && targetId === path.path[i])) {
              return '#ff6b6b';
            }
          }
        }
        return '#999';
      })
      .style('stroke-width', d => {
        if (path && path.path.length > 1) {
          for (let i = 0; i < path.path.length - 1; i++) {
            const sourceId = typeof d.source === 'string' ? d.source : d.source.id;
            const targetId = typeof d.target === 'string' ? d.target : d.target.id;
            if ((sourceId === path.path[i] && targetId === path.path[i + 1]) ||
                (sourceId === path.path[i + 1] && targetId === path.path[i])) {
              return 4;
            }
          }
        }
        return 2;
      })
      .style('opacity', 0.8);

    const edgeLabels = g.append('g')
      .attr('class', 'edge-labels')
      .selectAll('text')
      .data(edges)
      .enter()
      .append('text')
      .attr('class', 'edge-label')
      .style('font-size', '12px')
      .style('fill', '#666')
      .style('text-anchor', 'middle')
      .style('dominant-baseline', 'central')
      .style('pointer-events', 'none')
      .text(d => d.weight.toString());

    const node = g.append('g')
      .attr('class', 'nodes')
      .selectAll('circle')
      .data(nodes)
      .enter()
      .append('circle')
      .attr('class', 'node')
      .attr('r', 18)
      .style('fill', d => {
        if (selectedNodes?.source === d.id) return '#4ecdc4';
        if (selectedNodes?.target === d.id) return '#ff6b6b';
        if (path && path.path.includes(d.id)) return '#ffd93d';
        return '#69b3a2';
      })
      .style('stroke', '#fff')
      .style('stroke-width', 2)
      .style('cursor', 'pointer')
      .call(d3.drag<SVGCircleElement, Node>()
        .on('start', (event, d) => {
          if (!event.active) sim.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on('drag', (event, d) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on('end', (event, d) => {
          if (!event.active) sim.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        })
      )
      .on('click', (event, d) => {
        if (onNodeClick) {
          onNodeClick(d.id);
        }
      });

    const nodeLabels = g.append('g')
      .attr('class', 'node-labels')
      .selectAll('text')
      .data(nodes)
      .enter()
      .append('text')
      .attr('class', 'node-label')
      .style('font-size', '14px')
      .style('font-weight', 'bold')
      .style('fill', '#333')
      .style('text-anchor', 'middle')
      .style('dominant-baseline', 'central')
      .style('pointer-events', 'none')
      .text(d => d.id);

    sim.on('tick', () => {
      link
        .attr('x1', d => (d.source as Node).x!)
        .attr('y1', d => (d.source as Node).y!)
        .attr('x2', d => (d.target as Node).x!)
        .attr('y2', d => (d.target as Node).y!);

      edgeLabels
        .attr('x', d => ((d.source as Node).x! + (d.target as Node).x!) / 2)
        .attr('y', d => ((d.source as Node).y! + (d.target as Node).y!) / 2);

      node
        .attr('cx', d => d.x!)
        .attr('cy', d => d.y!);

      nodeLabels
        .attr('x', d => d.x!)
        .attr('y', d => d.y!);
    });

    return () => {
      if (sim) {
        sim.stop();
      }
      // ensure ref cleared on unmount
      simulationRef.current = null;
    };
  }, [graph, path, selectedNodes, width, height, onNodeClick]);

  return (
    <div className="w-full h-full">
      <svg
        ref={svgRef}
        width={width}
        height={height}
        className="border border-slate-300 rounded-lg bg-slate-50 shadow-sm"
        viewBox={`0 0 ${width} ${height}`}
        preserveAspectRatio="xMidYMid meet"
      />
      {path && (
        <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="space-y-2 text-sm">
            <div>
              <span className="font-semibold text-green-800">Path:</span>
              <span className="ml-2 font-mono text-green-700">{path.path.join(' → ')}</span>
            </div>
            <div>
              <span className="font-semibold text-green-800">Distance:</span>
              <span className="ml-2 font-mono text-green-700">{path.distance}</span>
            </div>
            <div>
              <span className="font-semibold text-green-800">Algorithm:</span>
              <span className="ml-2 text-green-700 capitalize">{path.algorithm_used}</span>
            </div>
            <div>
              <span className="font-semibold text-green-800">Time:</span>
              <span className="ml-2 text-green-700">{path.execution_time_ms.toFixed(2)}ms</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GraphVisualization;
