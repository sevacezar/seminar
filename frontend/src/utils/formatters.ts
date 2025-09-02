// Утилиты для форматирования данных

import { CHART_COLORS } from './constants';
import { Unit } from '../types/api';

export interface FormattedNumber {
  value: number;
  unit: string;
  suffix: string;
}

// Форматирование больших чисел для оси Y
export function formatLargeNumber(value: number, unit: Unit): FormattedNumber {
  const absValue = Math.abs(value);
  const isMeters = unit === Unit.CUBIC_METERS;
  
  if (absValue >= 1000000000) {
    return {
      value: Number((value / 1000000000).toFixed(1)),
      unit: isMeters ? 'млрд. м³' : 'млрд. т',
      suffix: 'млрд.'
    };
  } else if (absValue >= 1000000) {
    return {
      value: Number((value / 1000000).toFixed(1)),
      unit: isMeters ? 'млн. м³' : 'млн. т',
      suffix: 'млн.'
    };
  } else if (absValue >= 1000) {
    return {
      value: Number((value / 1000).toFixed(1)),
      unit: isMeters ? 'тыс. м³' : 'тыс. т',
      suffix: 'тыс.'
    };
  }
  
  return {
    value: Number(value.toFixed(1)),
    unit: unit,
    suffix: ''
  };
}

// Форматирование значений для отображения на графике
export function formatValueForDisplay(value: number, unit: Unit): string {
  const formatted = formatLargeNumber(value, unit);
  return `${formatted.value} ${formatted.suffix}`.trim();
}

// Генерация цветов для месторождений в корпоративной палитре Газпрома
export function generateFieldColors(fieldCount: number): string[] {
  const colors: string[] = [];
  for (let i = 0; i < fieldCount; i++) {
    colors.push(CHART_COLORS[i % CHART_COLORS.length]);
  }
  
  return colors;
}

// Форматирование дат для оси X
export function formatDateForAxis(date: string, aggregationStep: string): string {
  if (aggregationStep === 'год') {
    return date; // Уже в формате "2023"
  } else if (aggregationStep === 'квартал') {
    return date; // В формате "2023-Q1"
  } else if (aggregationStep === 'месяц') {
    const [year, month] = date.split('-');
    const monthNames = [
      'Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн',
      'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек'
    ];
    return `${monthNames[parseInt(month) - 1]} ${year}`;
  }
  
  return date;
}

// Проверка корректности диапазона дат
export function isValidDateRange(dateFrom: string, dateTo: string): boolean {
  if (!dateFrom || !dateTo) return false;
  
  const from = new Date(dateFrom);
  const to = new Date(dateTo);
  
  return from <= to;
}

// Преобразование даты в формат для API (YYYY-MM-01)
export function formatDateForApi(year: number, month: number): string {
  return `${year}-${month.toString().padStart(2, '0')}-01`;
}
