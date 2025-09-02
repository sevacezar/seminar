import React from 'react';
import {
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  Divider
} from '@mui/material';
import {
  TrendingUp,
  LocationOn,
  DateRange,
  Assessment
} from '@mui/icons-material';

import { ProductionDynamicsResponse } from '../types/api';
import { formatValueForDisplay } from '../utils/formatters';

interface StatisticsPanelProps {
  data: ProductionDynamicsResponse | null;
}

const StatisticsPanel: React.FC<StatisticsPanelProps> = ({ data }) => {
  if (!data) return null;

  const { metadata, fields, total } = data;
  const unit = metadata.response.unit;
  
  // Вычисляем статистики
  const totalProduction = total.production_by_period[total.production_by_period.length - 1] || 0;
  const averagePerField = fields.length > 0 ? totalProduction / fields.length : 0;
  
  // Находим месторождение с максимальной добычей
  const fieldWithMaxProduction = fields.reduce((max, field) => {
    const fieldTotal = field.production_by_period[field.production_by_period.length - 1] || 0;
    const maxTotal = max.production_by_period[max.production_by_period.length - 1] || 0;
    return fieldTotal > maxTotal ? field : max;
  }, fields[0]);

  const maxFieldProduction = fieldWithMaxProduction 
    ? fieldWithMaxProduction.production_by_period[fieldWithMaxProduction.production_by_period.length - 1] || 0
    : 0;

  const statisticCards = [
    {
      title: 'Общая добыча',
      value: formatValueForDisplay(totalProduction, unit),
      icon: <Assessment sx={{ fontSize: 40, color: '#003f7f' }} />,
      color: '#003f7f'
    },
    {
      title: 'Месторождений',
      value: metadata.response.total_fields.toString(),
      icon: <LocationOn sx={{ fontSize: 40, color: '#0066cc' }} />,
      color: '#0066cc'
    },
    {
      title: 'Периодов',
      value: metadata.response.total_periods.toString(),
      icon: <DateRange sx={{ fontSize: 40, color: '#4d94ff' }} />,
      color: '#4d94ff'
    },
    {
      title: 'Средняя добыча',
      value: formatValueForDisplay(averagePerField, unit),
      icon: <TrendingUp sx={{ fontSize: 40, color: '#006600' }} />,
      color: '#006600'
    }
  ];

  return (
    <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom color="primary" sx={{ fontWeight: 600, mb: 3 }}>
        Сводная статистика
      </Typography>
      
      <Box sx={{ 
        display: 'flex', 
        flexWrap: 'wrap', 
        gap: 3,
        '& > *': { 
          flex: '1 1 250px',
          minWidth: '200px'
        }
      }}>
        {statisticCards.map((card, index) => (
          <Card 
            key={index}
            elevation={1} 
            sx={{ 
              borderLeft: `4px solid ${card.color}`,
              transition: 'transform 0.2s, box-shadow 0.2s',
              '&:hover': {
                transform: 'translateY(-2px)',
                boxShadow: 3
              }
            }}
          >
            <CardContent sx={{ textAlign: 'center', py: 2 }}>
              <Box sx={{ mb: 1 }}>
                {card.icon}
              </Box>
              <Typography variant="h4" sx={{ fontWeight: 700, color: card.color, mb: 0.5 }}>
                {card.value}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {card.title}
              </Typography>
            </CardContent>
          </Card>
        ))}
      </Box>

      {/* Дополнительная информация */}
      <Divider sx={{ my: 3 }} />
      
      <Box sx={{ 
        display: 'flex', 
        flexWrap: 'wrap', 
        gap: 3,
        '& > *': { 
          flex: '1 1 300px',
          minWidth: '250px'
        }
      }}>
        <Box sx={{ p: 2, backgroundColor: '#f8f9fa', borderRadius: 2 }}>
          <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1, color: '#003f7f' }}>
            Лидер по добыче
          </Typography>
          <Typography variant="body1" sx={{ fontWeight: 500 }}>
            {fieldWithMaxProduction?.field_name}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {formatValueForDisplay(maxFieldProduction, unit)}
          </Typography>
        </Box>
        
        <Box sx={{ p: 2, backgroundColor: '#f8f9fa', borderRadius: 2 }}>
          <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1, color: '#003f7f' }}>
            Параметры анализа
          </Typography>
          <Typography variant="body2" color="text.secondary">
            <strong>Флюид:</strong> {metadata.request.fluid_type}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            <strong>Период:</strong> {metadata.request.date_from} — {metadata.request.date_to}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            <strong>Шаг:</strong> {metadata.request.aggregation_step}
          </Typography>
        </Box>
      </Box>
    </Paper>
  );
};

export default StatisticsPanel;
