import React, { useMemo } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  TooltipItem
} from 'chart.js';
import ChartDataLabels from 'chartjs-plugin-datalabels';
import { Bar } from 'react-chartjs-2';
import { Box, Paper, Typography, CircularProgress } from '@mui/material';

import { ProductionDynamicsResponse, Unit } from '../types/api';
import { 
  formatLargeNumber, 
  formatValueForDisplay, 
  generateFieldColors, 
  formatDateForAxis 
} from '../utils/formatters';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ChartDataLabels
);

interface ProductionChartProps {
  data: ProductionDynamicsResponse | null;
  loading: boolean;
  error?: string;
}

const ProductionChart: React.FC<ProductionChartProps> = ({ data, loading, error }) => {
  const chartData = useMemo(() => {
    if (!data || !data.fields.length) return null;

    const labels = data.reporting_dates.map(date => 
      formatDateForAxis(date, data.metadata.request.aggregation_step)
    );
    
    const colors = generateFieldColors(data.fields.length);
    
    // Создаем датасеты для стекового графика - используем дифференциальные данные
    const datasets = data.fields.map((field, index) => {
      return {
        label: field.field_name,
        data: field.production_by_period, // Используем дифференциальные данные как есть
        backgroundColor: colors[index] + '80', // Прозрачность для заливки
        borderColor: colors[index],
        borderWidth: 1,
        stack: 'production', // Ключ для стекового графика
      };
    });

    return {
      labels,
      datasets,
    };
  }, [data]);

  const chartOptions = useMemo(() => {
    if (!chartData || !data) return {};

    const unit = data.metadata.response.unit;
    
    // Для стекового графика нужно найти максимальную сумму по периодам
    const maxStackValue = Math.max(...data.total.production_by_period);
    
    const formatted = formatLargeNumber(maxStackValue, unit);
    const yAxisUnit = formatted.unit;

    return {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index' as const,
        intersect: false,
      },
      scales: {
        x: {
          stacked: true,
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
          stacked: true,
          display: true,
          title: {
            display: true,
            text: `Добыча ${data.metadata.request.fluid_type === 'газ' ? 'газа' : 
                         data.metadata.request.fluid_type === 'нефть' ? 'нефти' : 'конденсата'}, ${yAxisUnit}`,
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
              return formatValueForDisplay(Number(value), unit);
            }
          },
          beginAtZero: true,
        },
      },
      plugins: {
        title: {
          display: true,
          text: 'Динамика добычи',
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
            title: (context: TooltipItem<'bar'>[]) => {
              return `Период: ${context[0].label}`;
            },
            label: (context: TooltipItem<'bar'>) => {
              const value = context.parsed.y;
              const formattedValue = formatValueForDisplay(value, unit);
              return `${context.dataset.label}: ${formattedValue}`;
            },
            footer: (context: TooltipItem<'bar'>[]) => {
              const total = context.reduce((sum, item) => sum + item.parsed.y, 0);
              const formattedTotal = formatValueForDisplay(total, unit);
              return `Общий объем: ${formattedTotal}`;
            }
          },
        },
        datalabels: {
          display: function(context: any) {
            // Показываем только для верхнего датасета (последнего месторождения в стеке)
            return context.datasetIndex === context.chart.data.datasets.length - 1;
          },
          align: 'top' as const,
          anchor: 'end' as const,
          formatter: function(value: number, context: any) {
            // Вычисляем сумму всех месторождений для данного периода
            const periodIndex = context.dataIndex;
            const totalValue = data.total.production_by_period[periodIndex];
            return formatValueForDisplay(totalValue, unit);
          },
          font: {
            weight: 'bold' as const,
            size: 12
          },
          color: '#003f7f',
          backgroundColor: 'rgba(255, 255, 255, 0.8)',
          borderColor: '#003f7f',
          borderRadius: 4,
          borderWidth: 1,
          padding: 4
        }
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
      <Paper elevation={2} sx={{ p: 4, textAlign: 'center', height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
        <CircularProgress size={60} sx={{ color: '#003f7f' }} />
        <Typography variant="h6" sx={{ mt: 2, color: '#666' }}>
          Загрузка данных...
        </Typography>
      </Paper>
    );
  }

  if (error) {
    return (
      <Paper elevation={2} sx={{ p: 4, textAlign: 'center', height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
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
      <Paper elevation={2} sx={{ p: 4, textAlign: 'center', height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
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
    <Paper elevation={2} sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ position: 'relative', flex: 1, minHeight: 0 }}>
        <Bar data={chartData} options={{...chartOptions, maintainAspectRatio: false}} />
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
