import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Divider,
  Card,
  CardContent,
} from '@mui/material';
import {
  useGetCurrentTransitsQuery,
  useGetMoonInfoQuery,
  type Transit,
  type MoonInfo,
  type PredictiveEvent,
} from '../services/api.new';

// Define the MoonInfo interface with all required properties
interface ExtendedMoonInfo extends MoonInfo {
  illumination: number;
  mansion: {
    number: number;
    name: string;
  };
  nextFullMoon: string;
  nextNewMoon: string;
}

const Dashboard: React.FC = () => {
  const today = new Date().toISOString().split('T')[0];
  const nextMonth = new Date();
  nextMonth.setMonth(nextMonth.getMonth() + 1);

  const { 
    data: currentTransitsResponse, 
    isLoading: transitsLoading,
    error: transitsError 
  } = useGetCurrentTransitsQuery();
  
  const { 
    data: moonInfoResponse, 
    isLoading: moonLoading,
    error: moonError 
  } = useGetMoonInfoQuery();

  // Extract data from API responses
  const currentTransits = currentTransitsResponse?.data;
  const moonInfo = moonInfoResponse?.data as ExtendedMoonInfo;

  // Mock upcoming events since the query doesn't exist yet
  const upcomingEvents: PredictiveEvent[] = [
    {
      startDate: today,
      endDate: nextMonth.toISOString().split('T')[0],
      description: 'Mercury Retrograde in Gemini',
      type: 'Planetary Motion',
      significance: 'High'
    },
    {
      startDate: today,
      endDate: nextMonth.toISOString().split('T')[0],
      description: 'Venus conjunct Jupiter',
      type: 'Planetary Aspect',
      significance: 'Medium'
    }
  ];

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Cosmic Oracle Dashboard
      </Typography>

      <Grid container spacing={3}>
        {/* Current Transits */}
        <Grid item xs={12} md={6}>
          <Card elevation={3}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Current Planetary Positions
              </Typography>
              {transitsLoading ? (
                <Box display="flex" justifyContent="center" p={2}>
                  <CircularProgress />
                </Box>
              ) : transitsError ? (
                <Typography color="error">
                  Error loading transit data
                </Typography>
              ) : currentTransits && currentTransits.length > 0 ? (
                <List>
                  {currentTransits.map((transit: Transit, index: number) => (
                    <React.Fragment key={`${transit.planet}-${index}`}>
                      <ListItem>
                        <ListItemText
                          primary={transit.planet}
                          secondary={`${transit.sign} (House ${transit.house})`}
                        />
                      </ListItem>
                      {index < currentTransits.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              ) : (
                <Typography>No transit data available</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Lunar Information */}
        <Grid item xs={12} md={6}>
          <Card elevation={3}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Lunar Status
              </Typography>
              {moonLoading ? (
                <Box display="flex" justifyContent="center" p={2}>
                  <CircularProgress />
                </Box>
              ) : moonError ? (
                <Typography color="error">
                  Error loading moon data
                </Typography>
              ) : moonInfo ? (
                <List>
                  <ListItem>
                    <ListItemText
                      primary="Moon Phase"
                      secondary={
                        moonInfo.illumination 
                          ? `${moonInfo.phase} (${(moonInfo.illumination * 100).toFixed(1)}% illuminated)`
                          : moonInfo.phase
                      }
                    />
                  </ListItem>
                  <Divider />
                  <ListItem>
                    <ListItemText
                      primary="Moon Sign"
                      secondary={moonInfo.sign}
                    />
                  </ListItem>
                  <Divider />
                  <ListItem>
                    <ListItemText
                      primary="Moon House"
                      secondary={`House ${moonInfo.house}`}
                    />
                  </ListItem>
                  {moonInfo.mansion && (
                    <>
                      <Divider />
                      <ListItem>
                        <ListItemText
                          primary="Lunar Mansion"
                          secondary={`${moonInfo.mansion.number} - ${moonInfo.mansion.name}`}
                        />
                      </ListItem>
                    </>
                  )}
                  {moonInfo.nextFullMoon && (
                    <>
                      <Divider />
                      <ListItem>
                        <ListItemText
                          primary="Next Full Moon"
                          secondary={new Date(moonInfo.nextFullMoon).toLocaleDateString()}
                        />
                      </ListItem>
                    </>
                  )}
                  {moonInfo.nextNewMoon && (
                    <>
                      <Divider />
                      <ListItem>
                        <ListItemText
                          primary="Next New Moon"
                          secondary={new Date(moonInfo.nextNewMoon).toLocaleDateString()}
                        />
                      </ListItem>
                    </>
                  )}
                </List>
              ) : (
                <Typography>No moon data available</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Upcoming Events */}
        <Grid item xs={12}>
          <Card elevation={3}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Upcoming Astrological Events
              </Typography>
              {upcomingEvents && upcomingEvents.length > 0 ? (
                <List>
                  {upcomingEvents.map((event: PredictiveEvent, index: number) => (
                    <React.Fragment key={`event-${index}`}>
                      <ListItem>
                        <ListItemText
                          primary={event.type}
                          secondary={
                            <Box>
                              <Typography variant="body2" color="text.secondary">
                                {new Date(event.startDate).toLocaleDateString()} - {' '}
                                {new Date(event.endDate).toLocaleDateString()}
                              </Typography>
                              <Typography variant="body2">
                                {event.description}
                              </Typography>
                              <Typography variant="caption" color="primary">
                                Significance: {event.significance}
                              </Typography>
                            </Box>
                          }
                        />
                      </ListItem>
                      {index < upcomingEvents.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              ) : (
                <Typography>No upcoming events found</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
