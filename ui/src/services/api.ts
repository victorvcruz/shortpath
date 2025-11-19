import { 
  Graph, 
  GraphInput, 
  GraphResponse, 
  PathQuery, 
  PathResult, 
  AlgorithmRecommendation
} from '../types/graph';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiError extends Error {
  constructor(public status: number, message: string, public details?: any) {
    super(message);
    this.name = 'ApiError';
  }
}

class ApiService {
  private async request<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        let errorData;
        try {
          errorData = await response.json();
        } catch {
          errorData = { message: 'Network error occurred' };
        }
        
        throw new ApiError(
          response.status, 
          errorData.message || `HTTP ${response.status}`,
          errorData
        );
      }

      if (response.status === 204) {
        return {} as T;
      }

      return await response.json();
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(0, 'Network error: ' + (error as Error).message);
    }
  }

  async healthCheck(): Promise<{ status: string; service: string; timestamp: string }> {
    return this.request('/health');
  }

  async createGraph(graphInput: GraphInput): Promise<GraphResponse> {
    return this.request('/graphs/', {
      method: 'POST',
      body: JSON.stringify(graphInput),
    });
  }

  async getGraph(graphId: string): Promise<Graph> {
    return this.request(`/graphs/${graphId}`);
  }

  async deleteGraph(graphId: string): Promise<void> {
    return this.request(`/graphs/${graphId}`, {
      method: 'DELETE',
    });
  }

  async validateGraph(graphId: string): Promise<any> {
    return this.request(`/graphs/${graphId}/validate`);
  }

  async getGraphComponents(graphId: string): Promise<any> {
    return this.request(`/graphs/${graphId}/components`);
  }

  async calculateShortestPath(
    graphId: string, 
    query: PathQuery
  ): Promise<PathResult> {
    return this.request(`/graphs/${graphId}/shortest-path`, {
      method: 'POST',
      body: JSON.stringify(query),
    });
  }

  async calculateAllPaths(
    graphId: string, 
    source: string, 
    algorithm: string = 'dijkstra'
  ): Promise<Record<string, number>> {
    return this.request(`/graphs/${graphId}/all-paths/${source}?algorithm=${algorithm}`, {
      method: 'POST',
    });
  }

  async getAlgorithmRecommendations(graphId: string): Promise<AlgorithmRecommendation> {
    return this.request(`/graphs/${graphId}/algorithm-recommendations`);
  }

  async benchmarkAlgorithms(
    graphId: string, 
    query: Omit<PathQuery, 'algorithm'>
  ): Promise<any> {
    return this.request(`/graphs/${graphId}/benchmark`, {
      method: 'POST',
      body: JSON.stringify(query),
    });
  }

  async ping(): Promise<boolean> {
    try {
      await this.healthCheck();
      return true;
    } catch {
      return false;
    }
  }

  isApiError(error: any): error is ApiError {
    return error instanceof ApiError;
  }

  getErrorMessage(error: any): string {
    if (this.isApiError(error)) {
      return error.message;
    }
    return error?.message || 'An unexpected error occurred';
  }
}

export const apiService = new ApiService();
export { ApiError };
export default apiService;
