import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Grid,
  TextField,
  Typography,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Divider,
} from '@mui/material';
import type { BirthChart as BirthChartType } from '../types/astronomical';
import { useGetBirthChartQuery, useGetPlanetaryDignitiesQuery } from '../services/api';
import type { PlanetaryDignity } from '../services/api';
import type { Planet, House, Aspect } from '../types/astronomical';

interface ChartFormData {
  date: string;
  time: string;
  latitude: string;
  longitude: string;
}

const BirthChart: React.FC = () => {
  const [formData, setFormData] = useState<ChartFormData>({
    date: '',
    time: '',
    latitude: '',
    longitude: '',
  });

  const [error, setError] = React.useState<string | null>(null);

  const {
    data: birthChart,
    error: birthChartError,
    isLoading: isLoadingChart,
  } = useGetBirthChartQuery({
    date: formData.date,
    time: formData.time,
    latitude: parseFloat(formData.latitude) || 0,
    longitude: parseFloat(formData.longitude) || 0,
  }, {
    skip: !formData.date || !formData.time || !formData.latitude || !formData.longitude
  });

  const {
    data: dignities,
    isLoading: isLoadingDignities,
  } = useGetPlanetaryDignitiesQuery({
    date: formData.date,
    time: formData.time,
  }, {
    skip: !formData.date || !formData.time
  });

  React.useEffect(() => {
    if (birthChartError) {
      setError('Error loading birth chart data. Please try again.');
    } else if (dignities?.length === 0) {
      setError('No planetary dignity data available.');
    } else {
      setError(null);
    }
  }, [birthChartError, dignities]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  const renderPlanetList = (planets: Planet[]) => (
    <List>
      {planets.map((planet) => (
        <ListItem key={planet.name}>
          <ListItemText
            primary={planet.name}
            secondary={`${planet.sign} ${planet.longitude.toFixed(2)}° ${
              planet.isRetrograde ? 'Rx' : ''
            } | House ${planet.house}`}
          />
        </ListItem>
      ))}
    </List>
  );

  const renderHouseList = (houses: House[]) => (
    <List>
      {houses.map((house) => (
        <ListItem key={house.number}>
          <ListItemText
            primary={`House ${house.number}`}
            secondary={`${house.sign} ${house.cusp.toFixed(2)}°`}
          />
        </ListItem>
      ))}
    </List>
  );

  const renderAspectList = (aspects: Aspect[]) => (
    <List>
      {aspects.map((aspect, index) => (
        <ListItem key={index}>
          <ListItemText
            primary={`${aspect.planet1} ${aspect.type} ${aspect.planet2}`}
            secondary={`Orb: ${aspect.orb.toFixed(2)}° | Nature: ${aspect.nature}`}
          />
        </ListItem>
      ))}
    </List>
  );

  const isLoading = isLoadingChart || isLoadingDignities;

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
        <CircularProgress size={60} thickness={4} />
      </Box>
    );
  }

  if (error) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
        <Typography color="error" variant="h6">{error}</Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Birth Chart Calculator
      </Typography>
      
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Grid container spacing={2}>
            <Grid component="div" item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Birth Date"
                type="date"
                name="date"
                value={formData.date}
                onChange={handleInputChange}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid component="div" item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Birth Time"
                type="time"
                name="time"
                value={formData.time}
                onChange={handleInputChange}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>

            <Grid component="div" item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Latitude"
                type="number"
                name="latitude"
                value={formData.latitude}
                onChange={handleInputChange}
                helperText="Decimal degrees (e.g., 51.5074 for London)"
              />
            </Grid>

            <Grid component="div" item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Longitude"
                type="number"
                name="longitude"
                value={formData.longitude}
                onChange={handleInputChange}
                helperText="Decimal degrees (e.g., -0.1278 for London)"
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {birthChart && (
        <Grid container spacing={4}>

          <Grid component="div" item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Planets
                </Typography>
                {renderPlanetList(birthChart.planets)}
              </CardContent>
            </Card>
          </Grid>
          

          <Grid component="div" item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Houses
                </Typography>
                {renderHouseList(birthChart.houses)}
              </CardContent>
            </Card>
          </Grid>
          

          <Grid component="div" item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Aspects
                </Typography>
                {renderAspectList(birthChart.aspects)}
              </CardContent>
            </Card>
          </Grid>
          
          {dignities && (

            <Grid component="div" item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Planetary Dignities
                  </Typography>
                  <List>
                    {dignities.map((dignity: PlanetaryDignity) => (
                      <React.Fragment key={dignity.planet}>
                        <ListItem>
                          <ListItemText
                            primary={dignity.planet}
                            secondary={`
                              Essential: ${dignity.essential.score.toFixed(2)} |
                              Accidental: ${dignity.accidental.score.toFixed(2)} |
                              Total: ${(dignity.essential.score + dignity.accidental.score).toFixed(2)}
                            `}
                          />
                        </ListItem>
                        <Divider />
                      </React.Fragment>
                    ))}
                  </List>
                </CardContent>
              </Card>
            </Grid>
          )}
        </Grid>
      )}
    </Box>
  );

};
export default BirthChart;