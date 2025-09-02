import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  OutlinedInput,
  SelectChangeEvent
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import dayjs, { Dayjs } from 'dayjs';
import 'dayjs/locale/ru';

import { Field, FluidType, SedimentComplex, AggregationStep } from '../types/api';
import { formatDateForApi, isValidDateRange } from '../utils/formatters';

dayjs.locale('ru');

export interface FilterValues {
  selectedFields: number[];
  fluidType: FluidType;
  selectedComplexes: SedimentComplex[];
  dateFrom: string | null;
  dateTo: string | null;
  aggregationStep: AggregationStep;
}

interface FilterPanelProps {
  fields: Field[];
  onFiltersChange: (filters: FilterValues) => void;
  loading?: boolean;
}

const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
  PaperProps: {
    style: {
      maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
      width: 250,
    },
  },
};

const FilterPanel: React.FC<FilterPanelProps> = ({ fields, onFiltersChange, loading = false }) => {
  const [selectedFields, setSelectedFields] = useState<number[]>([]);
  const [fluidType, setFluidType] = useState<FluidType>(FluidType.GAS);
  const [selectedComplexes, setSelectedComplexes] = useState<SedimentComplex[]>([]);
  const [dateFrom, setDateFrom] = useState<Dayjs | null>(null);
  const [dateTo, setDateTo] = useState<Dayjs | null>(null);
  const [aggregationStep, setAggregationStep] = useState<AggregationStep>(AggregationStep.YEARLY);

  // Доступные значения
  const fluidTypes = [
    { value: FluidType.GAS, label: 'Газ' },
    { value: FluidType.OIL, label: 'Нефть' },
    { value: FluidType.CONDENSATE, label: 'Конденсат' }
  ];

  const sedimentComplexes = [
    { value: SedimentComplex.TURON, label: 'Турон' },
    { value: SedimentComplex.SENOMAN, label: 'Сеноман' },
    { value: SedimentComplex.NEOKOM, label: 'Неоком' },
    { value: SedimentComplex.ACH, label: 'Ачимовка' }
  ];

  const aggregationSteps = [
    { value: AggregationStep.MONTHLY, label: 'Месяц' },
    { value: AggregationStep.QUARTERLY, label: 'Квартал' },
    { value: AggregationStep.YEARLY, label: 'Год' }
  ];

  // Обновление фильтров при изменении значений
  useEffect(() => {
    const dateFromStr = dateFrom ? formatDateForApi(dateFrom.year(), dateFrom.month() + 1) : null;
    const dateToStr = dateTo ? formatDateForApi(dateTo.year(), dateTo.month() + 1) : null;

    // Проверяем валидность дат перед отправкой
    const isValidDates = !dateFromStr || !dateToStr || isValidDateRange(dateFromStr, dateToStr);
    
    onFiltersChange({
      selectedFields,
      fluidType,
      selectedComplexes,
      dateFrom: isValidDates ? dateFromStr : null,
      dateTo: isValidDates ? dateToStr : null,
      aggregationStep
    });
  }, [selectedFields, fluidType, selectedComplexes, dateFrom, dateTo, aggregationStep, onFiltersChange]);

  const handleFieldsChange = (event: SelectChangeEvent<typeof selectedFields>) => {
    const value = event.target.value;
    setSelectedFields(typeof value === 'string' ? value.split(',').map(Number) : value);
  };

  const handleComplexesChange = (event: SelectChangeEvent<typeof selectedComplexes>) => {
    const value = event.target.value;
    setSelectedComplexes(typeof value === 'string' ? value.split(',') as SedimentComplex[] : value);
  };

  const isValidFilters = () => {
    const hasValidSelections = selectedFields.length > 0 && selectedComplexes.length > 0;
    const hasValidDates = dateFrom && dateTo;
    const hasValidDateRange = hasValidDates && isValidDateRange(
      formatDateForApi(dateFrom.year(), dateFrom.month() + 1),
      formatDateForApi(dateTo.year(), dateTo.month() + 1)
    );
    
    return hasValidSelections && hasValidDateRange;
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDayjs} adapterLocale="ru">
      <Paper elevation={2} sx={{ p: 3, backgroundColor: '#f8f9fa', height: '100%', overflow: 'auto' }}>
        <Typography variant="h6" gutterBottom color="primary" sx={{ fontWeight: 600, mb: 3 }}>
          Параметры анализа
        </Typography>
        
        {/* Первый столбец - Месторождения */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2, color: '#003f7f' }}>
            Месторождения
          </Typography>
          <FormControl fullWidth>
            <InputLabel>Выберите месторождения</InputLabel>
            <Select
              multiple
              value={selectedFields}
              onChange={handleFieldsChange}
              input={<OutlinedInput label="Выберите месторождения" />}
              renderValue={(selected) => (
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {selected.map((value) => {
                    const field = fields.find(f => f.id === value);
                    return (
                      <Chip
                        key={value}
                        label={field?.name || `ID: ${value}`}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    );
                  })}
                </Box>
              )}
              MenuProps={MenuProps}
              disabled={loading}
            >
              {fields.map((field) => (
                <MenuItem key={field.id} value={field.id}>
                  {field.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>

        {/* Второй столбец - Остальные параметры */}
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          {/* Комплексы отложений */}
          <Box>
            <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, color: '#003f7f' }}>
              Комплексы отложений
            </Typography>
            <FormControl fullWidth>
              <InputLabel>Выберите комплексы</InputLabel>
              <Select
                multiple
                value={selectedComplexes}
                onChange={handleComplexesChange}
                input={<OutlinedInput label="Выберите комплексы" />}
                renderValue={(selected) => (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {selected.map((value) => (
                      <Chip
                        key={value}
                        label={sedimentComplexes.find(c => c.value === value)?.label || value}
                        size="small"
                        color="secondary"
                        variant="outlined"
                      />
                    ))}
                  </Box>
                )}
                MenuProps={MenuProps}
                disabled={loading}
              >
                {sedimentComplexes.map((complex) => (
                  <MenuItem key={complex.value} value={complex.value}>
                    {complex.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>

          {/* Тип флюида */}
          <Box>
            <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, color: '#003f7f' }}>
              Тип флюида
            </Typography>
            <FormControl fullWidth>
              <InputLabel>Выберите флюид</InputLabel>
              <Select
                value={fluidType}
                onChange={(e) => setFluidType(e.target.value as FluidType)}
                label="Выберите флюид"
                disabled={loading}
              >
                {fluidTypes.map((type) => (
                  <MenuItem key={type.value} value={type.value}>
                    {type.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>

          {/* Шаг агрегации */}
          <Box>
            <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, color: '#003f7f' }}>
              Шаг построения
            </Typography>
            <FormControl fullWidth>
              <InputLabel>Выберите шаг</InputLabel>
              <Select
                value={aggregationStep}
                onChange={(e) => setAggregationStep(e.target.value as AggregationStep)}
                label="Выберите шаг"
                disabled={loading}
              >
                {aggregationSteps.map((step) => (
                  <MenuItem key={step.value} value={step.value}>
                    {step.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>

          {/* Даты */}
          <Box>
            <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, color: '#003f7f' }}>
              Период анализа
            </Typography>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <DatePicker
                label="Дата начала"
                value={dateFrom}
                onChange={setDateFrom}
                views={['year', 'month']}
                format="MM/YYYY"
                disabled={loading}
                slotProps={{
                  textField: {
                    size: 'small',
                    error: dateFrom && dateTo ? !isValidDateRange(
                      formatDateForApi(dateFrom.year(), dateFrom.month() + 1),
                      formatDateForApi(dateTo.year(), dateTo.month() + 1)
                    ) : false
                  }
                }}
              />
              <DatePicker
                label="Дата окончания"
                value={dateTo}
                onChange={setDateTo}
                views={['year', 'month']}
                format="MM/YYYY"
                disabled={loading}
                minDate={dateFrom || undefined}
                slotProps={{
                  textField: {
                    size: 'small',
                    error: dateFrom && dateTo ? !isValidDateRange(
                      formatDateForApi(dateFrom.year(), dateFrom.month() + 1),
                      formatDateForApi(dateTo.year(), dateTo.month() + 1)
                    ) : false
                  }
                }}
              />
            </Box>
          </Box>
        </Box>

        {/* Индикатор валидности */}
        {!isValidFilters() && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2" color="text.secondary">
              {selectedFields.length === 0 && "Выберите хотя бы одно месторождение. "}
              {selectedComplexes.length === 0 && "Выберите хотя бы один комплекс отложений. "}
              {(!dateFrom || !dateTo) && "Укажите начальную и конечную даты. "}
              {dateFrom && dateTo && !isValidDateRange(
                formatDateForApi(dateFrom.year(), dateFrom.month() + 1),
                formatDateForApi(dateTo.year(), dateTo.month() + 1)
              ) && "Конечная дата должна быть больше или равна начальной."}
            </Typography>
          </Box>
        )}
      </Paper>
    </LocalizationProvider>
  );
};

export default FilterPanel;
