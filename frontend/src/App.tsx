import React, { useCallback, useEffect } from 'react';
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  Container,
  AppBar,
  Toolbar,
  Typography,
  Box,
  Alert,
  Snackbar
} from '@mui/material';
import { ruRU } from '@mui/material/locale';

import FilterPanel, { FilterValues } from './components/FilterPanel';
import ProductionChart from './components/ProductionChart';
import { useProductionAnalytics } from './hooks/useProductionAnalytics';

// Создание кастомной темы в корпоративных цветах Газпрома
const gazpromTheme = createTheme({
  palette: {
    primary: {
      main: '#003f7f', // Основной синий Газпрома
      light: '#4d94ff',
      dark: '#002147',
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#0066cc',
      light: '#80b3ff',
      dark: '#004499',
      contrastText: '#ffffff',
    },
    background: {
      default: '#f5f7fa',
      paper: '#ffffff',
    },
    text: {
      primary: '#333333',
      secondary: '#666666',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
      color: '#003f7f',
    },
    h6: {
      fontWeight: 500,
    },
  },
  components: {
    MuiAppBar: {
      styleOverrides: {
        root: {
          background: 'linear-gradient(90deg, #003f7f 0%, #0066cc 100%)',
          boxShadow: '0 4px 20px rgba(0, 63, 127, 0.3)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 12,
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 16,
        },
      },
    },
  },
}, ruRU);

const App: React.FC = () => {
  const {
    fields,
    productionData,
    fieldsLoading,
    productionLoading,
    fieldsError,
    productionError,
    loadProductionData,
  } = useProductionAnalytics();

  // Обработка изменения фильтров
  const handleFiltersChange = useCallback((filters: FilterValues) => {
    loadProductionData(filters);
  }, [loadProductionData]);

  // Автоматическая загрузка данных при наличии валидных фильтров
  useEffect(() => {
    // Можно добавить дополнительную логику автозагрузки
  }, []);

  return (
    <ThemeProvider theme={gazpromTheme}>
      <CssBaseline />
      
      {/* Заголовок приложения */}
      <AppBar position="static" elevation={0}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 600 }}>
            Аналитика добычи углеводородов
          </Typography>
          <Typography variant="body2" sx={{ opacity: 0.9 }}>
            ПАО "Газпром"
          </Typography>
        </Toolbar>
      </AppBar>

      {/* Основной контент */}
      <Container maxWidth="xl" sx={{ py: 2, height: '100vh' }}>
        <Box sx={{ height: '100%' }}>
          {/* Заголовок страницы */}
          <Typography variant="h4" gutterBottom sx={{ mb: 4, textAlign: 'center' }}>
            Динамика добычи по месторождениям
          </Typography>

          {/* Ошибка загрузки месторождений */}
          {fieldsError && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {fieldsError}
            </Alert>
          )}

          {/* Основной контент с боковой панелью */}
          <Box sx={{ display: 'flex', gap: 3, height: 'calc(100vh - 200px)' }}>
            {/* Левая панель с фильтрами */}
            <Box sx={{ width: '400px', flexShrink: 0 }}>
              <FilterPanel
                fields={fields}
                onFiltersChange={handleFiltersChange}
                loading={fieldsLoading || productionLoading}
              />
            </Box>
            
            {/* Правая панель с графиком */}
            <Box sx={{ flex: 1, minWidth: 0 }}>
              <ProductionChart
                data={productionData}
                loading={productionLoading}
                error={productionError || undefined}
              />
            </Box>
          </Box>

          {/* Информационная панель */}
          <Box sx={{ mt: 4, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              Система аналитики производственных данных • Версия 1.0
            </Typography>
          </Box>
        </Box>
      </Container>

      {/* Уведомления об ошибках */}
      <Snackbar
        open={!!productionError}
        autoHideDuration={6000}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
      >
        <Alert severity="error" variant="filled">
          {productionError}
        </Alert>
      </Snackbar>
    </ThemeProvider>
  );
};

export default App;