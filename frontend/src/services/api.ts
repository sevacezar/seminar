import axios from 'axios';
import {
  Field,
  PaginatedResponse,
  ProductionDynamicsRequest,
  ProductionDynamicsResponse
} from '../types/api';

// Конфигурация API
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// Отладочная информация
console.log('🔧 API Configuration:');
console.log('  REACT_APP_API_URL:', process.env.REACT_APP_API_URL);
console.log('  API_BASE_URL:', API_BASE_URL);

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Обработка ошибок
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export class ApiService {
  // Получение списка месторождений
  static async getFields(params?: {
    operator?: string;
    name?: string;
    limit?: number;
    offset?: number;
  }): Promise<PaginatedResponse<Field>> {
    const response = await apiClient.get('/fields', { params });
    return response.data;
  }

  // Получение enum значений
  static async getFluidTypes(): Promise<string[]> {
    const response = await apiClient.get('/enums/fluid-types');
    return response.data;
  }

  static async getSedimentComplexes(): Promise<string[]> {
    const response = await apiClient.get('/enums/sediment-complexes');
    return response.data;
  }

  static async getAggregationSteps(): Promise<string[]> {
    const response = await apiClient.get('/enums/aggregation-steps');
    return response.data;
  }

  // Получение динамики добычи
  static async getProductionDynamics(
    params: ProductionDynamicsRequest
  ): Promise<ProductionDynamicsResponse> {
    const queryParams = new URLSearchParams();
    
    queryParams.append('date_from', params.date_from);
    queryParams.append('date_to', params.date_to);
    queryParams.append('fluid_type', params.fluid_type);
    queryParams.append('aggregation_step', params.aggregation_step);
    
    if (params.field_ids && params.field_ids.length > 0) {
      params.field_ids.forEach(id => queryParams.append('field_ids', id.toString()));
    }
    
    if (params.sediment_complexes && params.sediment_complexes.length > 0) {
      params.sediment_complexes.forEach(complex => 
        queryParams.append('sediment_complexes', complex)
      );
    }

    const response = await apiClient.get(`/analytics/production/dynamics?${queryParams.toString()}`);
    return response.data;
  }
}

export default ApiService;
