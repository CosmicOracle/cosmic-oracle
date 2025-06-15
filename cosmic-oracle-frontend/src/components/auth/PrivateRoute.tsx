import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';import { useSelector } from 'react-redux';
import { Box, CircularProgress } from '@mui/material';
import { RootState } from '../../store';

const PrivateRoute: React.FC = () => {
  const { isAuthenticated, token } = useSelector((state: RootState) => state.auth);
  const [isCheckingAuth, setIsCheckingAuth] = React.useState(true);

  React.useEffect(() => {
    // Here you could verify the token with a backend call
    // For now, we'll just simulate a check
    const checkAuth = async () => {
      setIsCheckingAuth(true);
      try {
        if (token) {
          // You could verify the token here
          // await api.verifyToken(token);
          setIsCheckingAuth(false);
        } else {
          setIsCheckingAuth(false);
        }
      } catch (error) {
        setIsCheckingAuth(false);
      }
    };

    checkAuth();
  }, [token]);

  if (isCheckingAuth) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
};

export default PrivateRoute;
