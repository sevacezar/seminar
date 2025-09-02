// Константы приложения

export const GAZPROM_COLORS = {
  primary: '#003f7f',
  secondary: '#0066cc',
  light: '#4d94ff',
  lighter: '#80b3ff',
  lightest: '#b3d1ff',
  green: '#006600',
  lightGreen: '#33cc33',
  brightGreen: '#66ff66',
  gray: '#666666',
  lightGray: '#999999',
  lighterGray: '#cccccc',
  teal: '#004d4d',
  lightTeal: '#008080',
  brightTeal: '#00cccc',
  lighterTeal: '#4dffff'
};

export const CHART_COLORS = [
  GAZPROM_COLORS.primary,
  GAZPROM_COLORS.secondary,
  GAZPROM_COLORS.light,
  GAZPROM_COLORS.lighter,
  GAZPROM_COLORS.lightest,
  GAZPROM_COLORS.green,
  GAZPROM_COLORS.lightGreen,
  GAZPROM_COLORS.brightGreen,
  GAZPROM_COLORS.gray,
  GAZPROM_COLORS.lightGray,
  GAZPROM_COLORS.lighterGray,
  GAZPROM_COLORS.teal,
  GAZPROM_COLORS.lightTeal,
  GAZPROM_COLORS.brightTeal,
  GAZPROM_COLORS.lighterTeal
];

export const FLUID_TYPE_LABELS = {
  'газ': 'Газ',
  'нефть': 'Нефть',
  'конденсат': 'Конденсат'
};

export const SEDIMENT_COMPLEX_LABELS = {
  'турон': 'Турон',
  'сеноман': 'Сеноман',
  'неоком': 'Неоком',
  'ачимовка': 'Ачимовка'
};

export const AGGREGATION_STEP_LABELS = {
  'месяц': 'Месяц',
  'квартал': 'Квартал',
  'год': 'Год'
};

export const API_ENDPOINTS = {
  FIELDS: '/fields',
  ENUMS: {
    FLUID_TYPES: '/enums/fluid-types',
    SEDIMENT_COMPLEXES: '/enums/sediment-complexes',
    AGGREGATION_STEPS: '/enums/aggregation-steps'
  },
  ANALYTICS: {
    PRODUCTION_DYNAMICS: '/analytics/production/dynamics'
  }
};

export const DATE_FORMATS = {
  API: 'YYYY-MM-DD',
  DISPLAY: 'MM/YYYY',
  CHART_YEAR: 'YYYY',
  CHART_MONTH: 'MMM YYYY',
  CHART_QUARTER: 'YYYY-[Q]Q'
};

export const CHART_CONFIG = {
  DEFAULT_HEIGHT: 500,
  ANIMATION_DURATION: 750,
  POINT_RADIUS: 4,
  POINT_HOVER_RADIUS: 6,
  BORDER_WIDTH: 2,
  TENSION: 0.1
};

export const VALIDATION_MESSAGES = {
  REQUIRED_FIELDS: 'Необходимо выбрать хотя бы одно месторождение',
  REQUIRED_COMPLEXES: 'Необходимо выбрать хотя бы один комплекс отложений',
  REQUIRED_DATES: 'Необходимо указать начальную и конечную даты',
  INVALID_DATE_RANGE: 'Конечная дата должна быть больше или равна начальной',
  NO_DATA: 'Нет данных для отображения с указанными параметрами'
};

export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Ошибка соединения с сервером',
  SERVER_ERROR: 'Внутренняя ошибка сервера',
  NOT_FOUND: 'Данные не найдены',
  VALIDATION_ERROR: 'Ошибка валидации данных',
  UNKNOWN_ERROR: 'Произошла неизвестная ошибка'
};
