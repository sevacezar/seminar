import React from 'react';
import {
  Box,
  CircularProgress,
  Typography,
  Backdrop
} from '@mui/material';

interface LoadingOverlayProps {
  loading: boolean;
  message?: string;
}

const LoadingOverlay: React.FC<LoadingOverlayProps> = ({ 
  loading, 
  message = 'Загрузка данных...' 
}) => {
  return (
    <Backdrop
      sx={{
        color: '#fff',
        zIndex: (theme) => theme.zIndex.drawer + 1,
        backgroundColor: 'rgba(0, 63, 127, 0.1)'
      }}
      open={loading}
    >
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 2,
          p: 4,
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          borderRadius: 2,
          backdropFilter: 'blur(4px)'
        }}
      >
        <CircularProgress 
          size={60} 
          sx={{ color: '#003f7f' }}
        />
        <Typography 
          variant="h6" 
          sx={{ 
            color: '#003f7f',
            fontWeight: 500,
            textAlign: 'center'
          }}
        >
          {message}
        </Typography>
      </Box>
    </Backdrop>
  );
};

export default LoadingOverlay;
