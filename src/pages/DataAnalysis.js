import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  CardHeader,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  CircularProgress,
  Alert,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
  Divider
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Analytics as AnalyticsIcon,
  Assessment as AssessmentIcon,
  Timeline as TimelineIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area
} from 'recharts';
import { getDataAnalysis, getPredictionAccuracy, getMarketTrends, getDataSources } from '../services/api';

const DataAnalysis = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedTimeframe, setSelectedTimeframe] = useState('30d');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [analysisData, setAnalysisData] = useState(null);
  const [accuracyData, setAccuracyData] = useState(null);
  const [marketTrends, setMarketTrends] = useState(null);
  const [dataSources, setDataSources] = useState([]);
  const [refreshing, setRefreshing] = useState(false);

  const timeframes = [
    { value: '7d', label: 'Last 7 Days' },
    { value: '30d', label: 'Last 30 Days' },
    { value: '90d', label: 'Last 3 Months' },
    { value: '1y', label: 'Last Year' }
  ];

  const categories = [
    { value: 'all', label: 'All Categories' },
    { value: 'Financial Markets', label: 'Financial Markets' },
    { value: 'Weather Patterns', label: 'Weather Patterns' },
    { value: 'Political Events', label: 'Political Events' },
    { value: 'Sports Outcomes', label: 'Sports Outcomes' },
    { value: 'Technology Trends', label: 'Technology Trends' },
    { value: 'Health Metrics', label: 'Health Metrics' },
    { value: 'Social Trends', label: 'Social Trends' },
    { value: 'Economic Indicators', label: 'Economic Indicators' }
  ];

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D', '#FFC658', '#FF7C7C'];

  useEffect(() => {
    fetchAllData();
  }, [selectedTimeframe, selectedCategory]);

  const fetchAllData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [analysisResponse, accuracyResponse, trendsResponse, sourcesResponse] = await Promise.all([
        getDataAnalysis({ timeframe: selectedTimeframe, category: selectedCategory }),
        getPredictionAccuracy({ timeframe: selectedTimeframe, category: selectedCategory }),
        getMarketTrends({ timeframe: selectedTimeframe }),
        getDataSources()
      ]);

      setAnalysisData(analysisResponse.data);
      setAccuracyData(accuracyResponse.data);
      setMarketTrends(trendsResponse.data);
      setDataSources(sourcesResponse.data);
    } catch (err) {
      console.error('Error fetching analysis data:', err);
      setError('Failed to load analysis data. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchAllData();
    setRefreshing(false);
  };

  const renderMetricCard = (title, value, change, icon, color = 'primary') => (
    <Card elevation={3}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box>
            <Typography color="textSecondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h4" component="div">
              {value}
            </Typography>
            {change !== undefined && (
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                {change >= 0 ? (
                  <TrendingUpIcon color="success" fontSize="small" />
                ) : (
                  <TrendingDownIcon color="error" fontSize="small" />
                )}
                <Typography
                  variant="body2"
                  color={change >= 0 ? 'success.main' : 'error.main'}
                  sx={{ ml: 0.5 }}
                >
                  {Math.abs(change)}%
                </Typography>
              </Box>
            )}
          </Box>
          <Box sx={{ color: `${color}.main` }}>
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  const renderAccuracyChart = () => {
    if (!accuracyData?.chartData) return null;

    return (
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={accuracyData.chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis domain={[0, 100]} />
          <Tooltip formatter={(value) => [`${value}%`, 'Accuracy']} />
          <Legend />
          <Line
            type="monotone"
            dataKey="accuracy"
            stroke="#8884d8"
            strokeWidth={2}
            dot={{ fill: '#8884d8' }}
          />
        </LineChart>
      </ResponsiveContainer>
    );
  };

  const renderCategoryDistribution = () => {
    if (!analysisData?.categoryDistribution) return null;

    return (
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={analysisData.categoryDistribution}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {analysisData.categoryDistribution.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
    );
  };

  const renderTrendChart = () => {
    if (!marketTrends?.trendData) return null;

    return (
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={marketTrends.trendData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Area
            type="monotone"
            dataKey="value"
            stroke="#82ca9d"
            fill="#82ca9d"
            fillOpacity={0.6}
          />
        </AreaChart>
      </ResponsiveContainer>
    );
  };

  const renderDataSourcesTable = () => (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Data Source</TableCell>
            <TableCell>Type</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Last Updated</TableCell>
            <TableCell>Reliability</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {dataSources.map((source) => (
            <TableRow key={source.id}>
              <TableCell>{source.name}</TableCell>
              <TableCell>{source.type}</TableCell>
              <TableCell>
                <Chip
                  label={source.status}
                  color={source.status === 'Active' ? 'success' : 'error'}
                  size="small"
                />
              </TableCell>
              <TableCell>
                {source.lastUpdated ? new Date(source.lastUpdated).toLocaleString() : 'N/A'}
              </TableCell>
              <TableCell>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <LinearProgress
                    variant="determinate"
                    value={source.reliability || 0}
                    sx={{ width: 100, mr: 1 }}
                  />
                  <Typography variant="body2">{source.reliability || 0}%</Typography>
                </Box>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
        <CircularProgress size={60} />
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Data Analysis</Typography>
        <Button
          variant="outlined"
          startIcon={refreshing ? <CircularProgress size={20} /> : <RefreshIcon />}
          onClick={handleRefresh}
          disabled={refreshing}
        >
          Refresh Data
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Filters */}
      <Paper elevation={2} sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth>
              <InputLabel>Timeframe</InputLabel>
              <Select
                value={selectedTimeframe}
                onChange={(e) => setSelectedTimeframe(e.target.value)}
                label="Timeframe"
              >
                {timeframes.map((timeframe) => (
                  <MenuItem key={timeframe.value} value={timeframe.value}>
                    {timeframe.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth>
              <InputLabel>Category</InputLabel>
              <Select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                label="Category"
              >
                {categories.map((category) => (
                  <MenuItem key={category.value} value={category.value}>
                    {category.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Paper>

      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          {renderMetricCard(
            'Total Predictions',
            analysisData?.totalPredictions || 0,
            analysisData?.predictionChange,
            <AnalyticsIcon fontSize="large" />,
            'primary'
          )}
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          {renderMetricCard(
            'Accuracy Rate',
            `${analysisData?.accuracyRate || 0}%`,
            analysisData?.accuracyChange,
            <AssessmentIcon fontSize="large" />,
            'success'
          )}
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          {renderMetricCard(
            'Active Data Sources',
            analysisData?.activeDataSources || 0,
            analysisData?.dataSourceChange,
            <TimelineIcon fontSize="large" />,
            'info'
          )}
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          {renderMetricCard(
            'Confidence Score',
            `${analysisData?.avgConfidence || 0}%`,
            analysisData?.confidenceChange,
            <TrendingUpIcon fontSize="large" />,
            'warning'
          )}
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Card elevation={3}>
            <CardHeader title="Prediction Accuracy Over Time" />
            <CardContent>
              {renderAccuracyChart()}
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card elevation={3}>
            <CardHeader title="Category Distribution" />
            <CardContent>
              {renderCategoryDistribution()}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12}>
          <Card elevation={3}>
            <CardHeader title="Market Trends" />
            <CardContent>
              {renderTrendChart()}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Data Sources */}
      <Card elevation={3}>
        <CardHeader title="Data Sources Status" />
        <CardContent>
          {renderDataSourcesTable()}
        </CardContent>
      </Card>
    </Box>
  );
};

export default DataAnalysis;