import React, { useMemo } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  TooltipItem
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { Box, Paper, Typography, CircularProgress } from '@mui/material';

import { ProductionDynamicsResponse } from '../types/api';
import { 
  formatLargeNumber, 
  formatValueForDisplay, 
  generateFieldColors, 
  formatDateForAxis 
} from '../utils/formatters';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface ProductionChartProps {
  data: ProductionDynamicsResponse | null;
  loading: boolean;
  error?: string;
}

const ProductionChart: React.FC<ProductionChartProps> = ({ data, loading, error }) => {
  const chartData = useMemo(() => {
    if (!data) return null;

    const colors = generateFieldColors(data.fields.length);
    const unit = data.metadata.response.unit;
    const aggregationStep = data.metadata.request.aggregation_step;

    // Подготовка меток для оси X
    const labels = data.reporting_dates.map(date => formatDateForAxis(date, aggregationStep));

    // Подготовка датасетов для каждого месторождения
    const datasets = data.fields.map((field, index) => {
      // Вычисляем накопительные значения
      const cumulativeData: number[] = [];
      let cumulative = 0;
      
      field.production_by_period.forEach(value => {
        cumulative += value;
        cumulativeData.push(cumulative);
      });

      return {
        label: field.field_name,
        data: cumulativeData,
        borderColor: colors[index],
        backgroundColor: colors[index] + '20', // Добавляем прозрачность
        fill: false,
        tension: 0.1,
        pointRadius: 4,
        pointHoverRadius: 6,
        borderWidth: 2,
      };
    });

    return {
      labels,
      datasets,
      unit
    };
  }, [data]);

  const chartOptions = useMemo(() => {
    if (!chartData || !data) return {};

    const unit = chartData.unit;
    const maxValue = Math.max(
      ...chartData.datasets.flatMap(dataset => dataset.data as number[])
    );
    
    const formatted = formatLargeNumber(maxValue, unit);
    const yAxisUnit = formatted.unit;
    const divisor = maxValue / formatted.value;

    return {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index' as const,
        intersect: false,
      },
      plugins: {
        title: {
          display: true,
          text: `Динамика добычи ${data.metadata.request.fluid_type} (накопительная)`,
          font: {
            size: 18,
            weight: 'bold' as const,
          },
          color: '#003f7f',
          padding: 20,
        },
        legend: {
          position: 'bottom' as const,
          labels: {
            usePointStyle: true,
            padding: 15,
            font: {
              size: 12,
            },
          },
        },
        tooltip: {
          mode: 'index' as const,
          intersect: false,
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          titleColor: '#003f7f',
          bodyColor: '#333',
          borderColor: '#003f7f',
          borderWidth: 1,
          cornerRadius: 8,
          displayColors: true,
          callbacks: {
            title: (context: TooltipItem<'line'>[]) => {
              return `Период: ${context[0].label}`;
            },
            label: (context: TooltipItem<'line'>) => {
              const value = context.parsed.y;
              const formattedValue = formatValueForDisplay(value, unit);
              return `${context.dataset.label}: ${formattedValue}`;
            },
            footer: (context: TooltipItem<'line'>[]) => {
              const total = context.reduce((sum, item) => sum + item.parsed.y, 0);
              const formattedTotal = formatValueForDisplay(total, unit);
              return `Общий объем: ${formattedTotal}`;
            }
          },
        },
      },
      scales: {
        x: {
          display: true,
          title: {
            display: true,
            text: 'Период',
            font: {
              size: 14,
              weight: 'bold' as const,
            },
            color: '#003f7f',
          },
          grid: {
            display: true,
            color: 'rgba(0, 63, 127, 0.1)',
          },
          ticks: {
            color: '#666',
            maxRotation: 45,
          },
        },
        y: {
          display: true,
          title: {
            display: true,
            text: yAxisUnit,
            font: {
              size: 14,
              weight: 'bold' as const,
            },
            color: '#003f7f',
          },
          grid: {
            display: true,
            color: 'rgba(0, 63, 127, 0.1)',
          },
          ticks: {
            color: '#666',
            callback: function(value: any) {
              const numValue = typeof value === 'number' ? value : parseFloat(value);
              return (numValue / divisor).toFixed(1);
            },
          },
        },
      },
      elements: {
        point: {
          hoverBackgroundColor: '#003f7f',
        },
      },
      // Отображение значений на точках графика
      onHover: (event: any, activeElements: any[]) => {
        const canvas = event.native?.target;
        if (canvas) {
          canvas.style.cursor = activeElements.length > 0 ? 'pointer' : 'default';
        }
      },
    };
  }, [chartData, data]);

  if (loading) {
    return (
      <Paper elevation={2} sx={{ p: 4, textAlign: 'center', minHeight: 400 }}>
        <CircularProgress size={60} sx={{ color: '#003f7f' }} />
        <Typography variant="h6" sx={{ mt: 2, color: '#666' }}>
          Загрузка данных...
        </Typography>
      </Paper>
    );
  }

  if (error) {
    return (
      <Paper elevation={2} sx={{ p: 4, textAlign: 'center', minHeight: 400 }}>
        <Typography variant="h6" color="error" gutterBottom>
          Ошибка загрузки данных
        </Typography>
        <Typography variant="body1" color="text.secondary">
          {error}
        </Typography>
      </Paper>
    );
  }

  if (!data || !chartData || data.fields.length === 0) {
    return (
      <Paper elevation={2} sx={{ p: 4, textAlign: 'center', minHeight: 400 }}>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          {!data ? 'Нет данных для отображения' : 'Данные не найдены'}
        </Typography>
        <Typography variant="body1" color="text.secondary">
          {!data 
            ? 'Выберите параметры для построения графика' 
            : 'Попробуйте изменить параметры фильтрации или выбрать другой период'}
        </Typography>
      </Paper>
    );
  }

  return (
    <Paper elevation={2} sx={{ p: 3 }}>
      <Box sx={{ position: 'relative', height: 500 }}>
        <Line data={chartData} options={chartOptions} />
      </Box>
      
      {/* Метаинформация */}
      <Box sx={{ mt: 2, p: 2, backgroundColor: '#f8f9fa', borderRadius: 1 }}>
        <Typography variant="body2" color="text.secondary">
          <strong>Месторождений:</strong> {data.metadata.response.total_fields} • 
          <strong> Периодов:</strong> {data.metadata.response.total_periods} • 
          <strong> Единица измерения:</strong> {data.metadata.response.unit} • 
          <strong> Сгенерировано:</strong> {new Date(data.metadata.response.generated_at).toLocaleString('ru-RU')}
        </Typography>
      </Box>
    </Paper>
  );
};

export default ProductionChart;
