import { useState, useEffect, useCallback } from 'react';
import { 
  Field, 
  ProductionDynamicsResponse, 
  ProductionDynamicsRequest
} from '../types/api';
import ApiService from '../services/api';
import { FilterValues } from '../components/FilterPanel';

export interface UseProductionAnalyticsState {
  // Данные
  fields: Field[];
  productionData: ProductionDynamicsResponse | null;
  
  // Состояния загрузки
  fieldsLoading: boolean;
  productionLoading: boolean;
  
  // Ошибки
  fieldsError: string | null;
  productionError: string | null;
  
  // Методы
  loadProductionData: (filters: FilterValues) => Promise<void>;
  clearProductionData: () => void;
}

export const useProductionAnalytics = (): UseProductionAnalyticsState => {
  // Состояние данных
  const [fields, setFields] = useState<Field[]>([]);
  const [productionData, setProductionData] = useState<ProductionDynamicsResponse | null>(null);
  
  // Состояния загрузки
  const [fieldsLoading, setFieldsLoading] = useState(true);
  const [productionLoading, setProductionLoading] = useState(false);
  
  // Ошибки
  const [fieldsError, setFieldsError] = useState<string | null>(null);
  const [productionError, setProductionError] = useState<string | null>(null);

  // Загрузка списка месторождений при инициализации
  useEffect(() => {
    const loadFields = async () => {
      try {
        setFieldsLoading(true);
        setFieldsError(null);
        
        const response = await ApiService.getFields({ limit: 1000 });
        setFields(response.data);
      } catch (error) {
        console.error('Error loading fields:', error);
        setFieldsError('Ошибка загрузки списка месторождений');
      } finally {
        setFieldsLoading(false);
      }
    };

    loadFields();
  }, []);

  // Загрузка данных о добыче
  const loadProductionData = useCallback(async (filters: FilterValues) => {
    // Проверка валидности фильтров
    if (!filters.selectedFields.length || 
        !filters.selectedComplexes.length || 
        !filters.dateFrom || 
        !filters.dateTo) {
      setProductionData(null);
      setProductionError(null);
      return;
    }

    try {
      setProductionLoading(true);
      setProductionError(null);
      
      const request: ProductionDynamicsRequest = {
        date_from: filters.dateFrom,
        date_to: filters.dateTo,
        fluid_type: filters.fluidType,
        field_ids: filters.selectedFields,
        sediment_complexes: filters.selectedComplexes,
        aggregation_step: filters.aggregationStep
      };

      const response = await ApiService.getProductionDynamics(request);
      setProductionData(response);
    } catch (error: any) {
      console.error('Error loading production data:', error);
      
      let errorMessage = 'Ошибка загрузки данных о добыче';
      
      if (error.response?.status === 404) {
        errorMessage = 'Данные не найдены для указанных параметров';
      } else if (error.response?.status === 400) {
        // Обработка ошибок валидации
        if (error.response?.data?.message) {
          errorMessage = error.response.data.message;
        } else {
          errorMessage = 'Некорректные параметры запроса';
        }
      } else if (error.response?.status === 422) {
        // Ошибки валидации Pydantic
        errorMessage = 'Ошибка валидации данных. Проверьте корректность введенных параметров.';
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message;
      }
      
      setProductionError(errorMessage);
      setProductionData(null);
    } finally {
      setProductionLoading(false);
    }
  }, []);

  // Очистка данных о добыче
  const clearProductionData = useCallback(() => {
    setProductionData(null);
    setProductionError(null);
  }, []);

  return {
    // Данные
    fields,
    productionData,
    
    // Состояния загрузки
    fieldsLoading,
    productionLoading,
    
    // Ошибки
    fieldsError,
    productionError,
    
    // Методы
    loadProductionData,
    clearProductionData,
  };
};
