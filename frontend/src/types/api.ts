// Типы для работы с API

export interface Field {
  id: number;
  name: string;
  operator: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  limit: number;
  offset: number;
}

// Enums
export enum FluidType {
  GAS = 'газ',
  OIL = 'нефть',
  CONDENSATE = 'конденсат'
}

export enum SedimentComplex {
  TURON = 'турон',
  SENOMAN = 'сеноман',
  NEOKOM = 'неоком',
  ACH = 'ачимовка'
}

export enum AggregationStep {
  MONTHLY = 'месяц',
  QUARTERLY = 'квартал',
  YEARLY = 'год'
}

export enum Unit {
  CUBIC_METERS = 'м3',
  TONS = 'т'
}

// Аналитика
export interface ProductionDynamicsRequest {
  date_from: string; // YYYY-MM-DD
  date_to: string; // YYYY-MM-DD
  fluid_type: FluidType;
  field_ids?: number[];
  sediment_complexes?: SedimentComplex[];
  aggregation_step: AggregationStep;
}

export interface FieldProductionData {
  field_id: number;
  field_name: string;
  production_by_period: number[];
}

export interface TotalProductionData {
  production_by_period: number[];
}

export interface ProductionDynamicsMetadataRequest {
  date_from: string;
  date_to: string;
  fluid_type: FluidType;
  field_ids?: number[];
  sediment_complexes?: SedimentComplex[];
  aggregation_step: AggregationStep;
}

export interface ProductionDynamicsMetadataResponse {
  total_fields: number;
  total_periods: number;
  unit: Unit;
  generated_at: string;
}

export interface ProductionDynamicsMetadata {
  request: ProductionDynamicsMetadataRequest;
  response: ProductionDynamicsMetadataResponse;
}

export interface ProductionDynamicsResponse {
  metadata: ProductionDynamicsMetadata;
  reporting_dates: string[];
  fields: FieldProductionData[];
  total: TotalProductionData;
}
