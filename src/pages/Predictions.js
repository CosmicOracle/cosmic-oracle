import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Chip,
  IconButton,
  Alert,
  CircularProgress,
  Snackbar
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as VisibilityIcon
} from '@mui/icons-material';
import { getPredictions, createPrediction, updatePrediction, deletePrediction, getPredictionById } from '../services/api';

const Predictions = () => {
  const [predictions, setPredictions] = useState([]);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [openViewDialog, setOpenViewDialog] = useState(false);
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  const [currentPrediction, setCurrentPrediction] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: '',
    confidence: 0,
    targetDate: '',
    dataSourceIds: []
  });
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success'
  });

  const categories = [
    'Financial Markets',
    'Weather Patterns',
    'Political Events',
    'Sports Outcomes',
    'Technology Trends',
    'Health Metrics',
    'Social Trends',
    'Economic Indicators'
  ];

  useEffect(() => {
    fetchPredictions();
  }, [page, rowsPerPage]);

  const fetchPredictions = async () => {
    try {
      setLoading(true);
      const response = await getPredictions({
        page: page + 1,
        limit: rowsPerPage
      });
      setPredictions(response.data.predictions);
      setTotalCount(response.data.totalCount);
      setError(null);
    } catch (err) {
      console.error('Error fetching predictions:', err);
      setError('Failed to load predictions. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleOpenDialog = (prediction = null) => {
    if (prediction) {
      setFormData({
        title: prediction.title,
        description: prediction.description,
        category: prediction.category,
        confidence: prediction.confidence,
        targetDate: prediction.targetDate.split('T')[0],
        dataSourceIds: prediction.dataSourceIds || []
      });
      setCurrentPrediction(prediction);
    } else {
      setFormData({
        title: '',
        description: '',
        category: '',
        confidence: 0,
        targetDate: '',
        dataSourceIds: []
      });
      setCurrentPrediction(null);
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
  };

  const handleOpenViewDialog = async (id) => {
    try {
      setLoading(true);
      const response = await getPredictionById(id);
      setCurrentPrediction(response.data);
      setOpenViewDialog(true);
    } catch (err) {
      console.error('Error fetching prediction details:', err);
      setSnackbar({
        open: true,
        message: 'Failed to load prediction details',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCloseViewDialog = () => {
    setOpenViewDialog(false);
  };

  const handleOpenDeleteDialog = (prediction) => {
    setCurrentPrediction(prediction);
    setOpenDeleteDialog(true);
  };

  const handleCloseDeleteDialog = () => {
    setOpenDeleteDialog(false);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleSubmit = async () => {
    try {
      setLoading(true);
      if (currentPrediction) {
        await updatePrediction(currentPrediction.id, formData);
        setSnackbar({
          open: true,
          message: 'Prediction updated successfully',
          severity: 'success'
        });
      } else {
        await createPrediction(formData);
        setSnackbar({
          open: true,
          message: 'Prediction created successfully',
          severity: 'success'
        });
      }
      handleCloseDialog();
      fetchPredictions();
    } catch (err) {
      console.error('Error saving prediction:', err);
      setSnackbar({
        open: true,
        message: 'Failed to save prediction',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    try {
      setLoading(true);
      await deletePrediction(currentPrediction.id);
      setSnackbar({
        open: true,
        message: 'Prediction deleted successfully',
        severity: 'success'
      });
      handleCloseDeleteDialog();
      fetchPredictions();
    } catch (err) {
      console.error('Error deleting prediction:', err);
      setSnackbar({
        open: true,
        message: 'Failed to delete prediction',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbar({
      ...snackbar,
      open: false
    });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Confirmed':
        return 'success';
      case 'Failed':
        return 'error';
      case 'Pending':
        return 'warning';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Predictions</Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          New Prediction
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Paper elevation={3}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Title</TableCell>
                <TableCell>Category</TableCell>
                <TableCell>Confidence</TableCell>
                <TableCell>Target Date</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading && page === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : predictions.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    No predictions found
                  </TableCell>
                </TableRow>
              ) : (
                predictions.map((prediction) => (
                  <TableRow key={prediction.id}>
                    <TableCell>{prediction.title}</TableCell>
                    <TableCell>{prediction.category}</TableCell>
                    <TableCell>{prediction.confidence}%</TableCell>
                    <TableCell>{new Date(prediction.targetDate).toLocaleDateString()}</TableCell>
                    <TableCell>
                      <Chip
                        label={prediction.status}
                        color={getStatusColor(prediction.status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <IconButton
                        color="primary"
                        onClick={() => handleOpenViewDialog(prediction.id)}
                        size="small"
                      >
                        <VisibilityIcon />
                      </IconButton>
                      <IconButton
                        color="secondary"
                        onClick={() => handleOpenDialog(prediction)}
                        size="small"
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton
                        color="error"
                        onClick={() => handleOpenDeleteDialog(prediction)}
                        size="small"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={totalCount}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Paper>

      {/* Create/Edit Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>{currentPrediction ? 'Edit Prediction' : 'Create New Prediction'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField
                name="targetDate"
                label="Target Date"
                type="date"
                fullWidth
                value={formData.targetDate}
                onChange={handleInputChange}
                InputLabelProps={{ shrink: true }}
                required
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained" disabled={loading}>
            {loading ? <CircularProgress size={20} /> : (currentPrediction ? 'Update' : 'Create')}
          </Button>
        </DialogActions>
      </Dialog>

      {/* View Dialog */}
      <Dialog open={openViewDialog} onClose={handleCloseViewDialog} maxWidth="md" fullWidth>
        <DialogTitle>Prediction Details</DialogTitle>
        <DialogContent>
          {currentPrediction && (
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                  {currentPrediction.title}
                </Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="body1" paragraph>
                  {currentPrediction.description}
                </Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2">Category:</Typography>
                <Typography variant="body2">{currentPrediction.category}</Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2">Confidence:</Typography>
                <Typography variant="body2">{currentPrediction.confidence}%</Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2">Target Date:</Typography>
                <Typography variant="body2">
                  {new Date(currentPrediction.targetDate).toLocaleDateString()}
                </Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2">Status:</Typography>
                <Chip
                  label={currentPrediction.status}
                  color={getStatusColor(currentPrediction.status)}
                  size="small"
                />
              </Grid>
              {currentPrediction.createdAt && (
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2">Created:</Typography>
                  <Typography variant="body2">
                    {new Date(currentPrediction.createdAt).toLocaleDateString()}
                  </Typography>
                </Grid>
              )}
              {currentPrediction.updatedAt && (
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2">Last Updated:</Typography>
                  <Typography variant="body2">
                    {new Date(currentPrediction.updatedAt).toLocaleDateString()}
                  </Typography>
                </Grid>
              )}
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseViewDialog}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={openDeleteDialog} onClose={handleCloseDeleteDialog}>
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete the prediction "{currentPrediction?.title}"?
            This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDeleteDialog}>Cancel</Button>
          <Button onClick={handleDelete} color="error" variant="contained" disabled={loading}>
            {loading ? <CircularProgress size={20} /> : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default Predictions;12}>
              <TextField
                name="title"
                label="Title"
                fullWidth
                value={formData.title}
                onChange={handleInputChange}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                name="description"
                label="Description"
                fullWidth
                multiline
                rows={4}
                value={formData.description}
                onChange={handleInputChange}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Category</InputLabel>
                <Select
                  name="category"
                  value={formData.category}
                  onChange={handleInputChange}
                  label="Category"
                  required
                >
                  {categories.map((category) => (
                    <MenuItem key={category} value={category}>
                      {category}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                name="confidence"
                label="Confidence (%)"
                type="number"
                fullWidth
                value={formData.confidence}
                onChange={handleInputChange}
                InputProps={{ inputProps: { min: 0, max: 100 } }}
                required
              />
            </Grid>
            <Grid item xs={