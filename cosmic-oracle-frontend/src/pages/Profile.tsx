import React from 'react';
import { Box, Typography, Paper, Grid } from '@mui/material';

const Profile: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Your Profile
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Personal Information
            </Typography>
            {/* TODO: Add profile information component */}
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Birth Details
            </Typography>
            {/* TODO: Add birth details component */}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Profile;
