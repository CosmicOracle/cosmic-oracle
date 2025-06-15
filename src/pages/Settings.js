import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  CardHeader,
  TextField,
  Button,
  Switch,
  FormControl,
  FormControlLabel,
  InputLabel,
  Select,
  MenuItem,
  Divider,
  Alert,
  CircularProgress,
  Snackbar,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  Save as SaveIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  ExpandMore as ExpandMoreIcon,
  Security as SecurityIcon,
  Notifications as NotificationsIcon,
  Palette as PaletteIcon,
  Language as LanguageIcon,
  Storage as StorageIcon,
  Api as ApiIcon
} from '@mui/icons-material';
import {
  getUserSettings,
  updateUserSettings,
  getSystemSettings,
  updateSystemSettings,
  getApiKeys,
  createApiKey,
  deleteApiKey
} from '../services/api';

const Settings = () => {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [userSettings, setUserSettings] = useState({
    theme: 'light',
    language: 'en',
    timezone: 'UTC',
    notifications: {
      email: true,
      push: false,
      predictions: true,
      reports: true
    },
    privacy: {
      shareData: false,
      analytics: true,
      marketing: false
    },
    display: {
      dateFormat: 'MM/DD/YYYY',
      timeFormat: '12h',
      currency: 'USD'
    },
    astrology: {
      houseSystem: 'placidus',
      aspectOrbs: {
        conjunction: 8,
        opposition: 8,
        trine: 6,
        square: 6,
        sextile: 4
      },
      showRetrogrades: true,
      showArabicParts: false
    }
  });
  const [systemSettings, setSystemSettings] = useState({});
  const [apiKeys, setApiKeys] = useState([]);
  const [showApiKeyDialog, setShowApiKeyDialog] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [selectedApiKey, setSelectedApiKey] = useState(null);
  const [newApiKey, setNewApiKey] = useState({ name: '', description: '' });
  const [showApiKeyValue, setShowApiKeyValue] = useState({});
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success'
  });

  const themes = [
    { value: 'light', label: 'Light' },
    { value: 'dark', label: 'Dark' },
    { value: 'auto', label: 'Auto (System)' }
  ];

  const languages = [
    { value: 'en', label: 'English' },
    { value: 'es', label: 'Español' },
    { value: 'fr', label: 'Français' },
    { value: 'de', label: 'Deutsch' },
    { value: 'it', label: 'Italiano' },
    { value: 'pt', label: 'Português' }
  ];

  const timezones = [
    { value: 'UTC', label: 'UTC' },
    { value: 'America/New_York', label: 'Eastern Time' },
    { value: 'America/Chicago', label: 'Central Time' },
    { value: 'America/Denver', label: 'Mountain Time' },
    { value: 'America/Los_Angeles', label: 'Pacific Time' },
    { value: 'Europe/London', label: 'London' },
    { value: 'Europe/Paris', label: 'Paris' },
    { value: 'Asia/Tokyo', label: 'Tokyo' },
    { value: 'Australia/Sydney', label: 'Sydney' }
  ];

  const houseSystems = [
    { value: 'placidus', label: 'Placidus' },
    { value: 'koch', label: 'Koch' },
    { value: 'whole_sign', label: 'Whole Sign' },
    { value: 'equal', label: 'Equal House' },
    { value: 'campanus', label: 'Campanus' },
    { value: 'regiomontanus', label: 'Regiomontanus' }
  ];

  const dateFormats = [
    { value: 'MM/DD/YYYY', label: 'MM/DD/YYYY' },
    { value: 'DD/MM/YYYY', label: 'DD/MM/YYYY' },
    { value: 'YYYY-MM-DD', label: 'YYYY-MM-DD' },
    { value: 'DD MMM YYYY', label: 'DD MMM YYYY' }
  ];

  const currencies = [
    { value: 'USD', label: 'US Dollar ($)' },
    { value: 'EUR', label: 'Euro (€)' },
    { value: 'GBP', label: 'British Pound (£)' },
    { value: 'JPY', label: 'Japanese Yen (¥)' },
    { value: 'CAD', label: 'Canadian Dollar (C$)' },
    { value: 'AUD', label: 'Australian Dollar (A$)' }
  ];

  useEffect(() => {
    fetchAllSettings();
  }, []);

  const fetchAllSettings = async () => {
    try {
      setLoading(true);
      const [userResponse, systemResponse, apiKeysResponse] = await Promise.all([
        getUserSettings(),
        getSystemSettings(),
        getApiKeys()
      ]);

      if (userResponse.data) {
        setUserSettings(prev => ({ ...prev, ...userResponse.data }));
      }
      if (systemResponse.data) {
        setSystemSettings(systemResponse.data);
      }
      if (apiKeysResponse.data) {
        setApiKeys(apiKeysResponse.data);
      }
      setError(null);
    } catch (err) {
      console.error('Error fetching settings:', err);
      setError('Failed to load settings. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const handleUserSettingChange = (section, field, value) => {
    setUserSettings(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value
      }
    }));
  };

  const handleDirectSettingChange = (field, value) => {
    setUserSettings(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleAspectOrbChange = (aspect, value) => {
    setUserSettings(prev => ({
      ...prev,
      astrology: {
        ...prev.astrology,
        aspectOrbs: {
          ...prev.astrology.aspectOrbs,
          [aspect]: parseFloat(value) || 0
        }
      }
    }));
  };

  const handleSaveSettings = async () => {
    try {
      setSaving(true);
      await updateUserSettings(userSettings);
      setSnackbar({
        open: true,
        message: 'Settings saved successfully',
        severity: 'success'
      });
    } catch (err) {
      console.error('Error saving settings:', err);
      setSnackbar({
        open: true,
        message: 'Failed to save settings',
        severity: 'error'
      });
    } finally {
      setSaving(false);
    }
  };

  const handleCreateApiKey = async () => {
    try {
      const response = await createApiKey(newApiKey);
      setApiKeys(prev => [...prev, response.data]);
      setNewApiKey({ name: '', description: '' });
      setShowApiKeyDialog(false);
      setSnackbar({
        open: true,
        message: 'API key created successfully',
        severity: 'success'
      });
    } catch (err) {
      console.error('Error creating API key:', err);
      setSnackbar({
        open: true,
        message: 'Failed to create API key',
        severity: 'error'
      });
    }
  };

  const handleDeleteApiKey = async () => {
    try {
      await deleteApiKey(selectedApiKey.id);
      setApiKeys(prev => prev.filter(key => key.id !== selectedApiKey.id));
      setShowDeleteDialog(false);
      setSelectedApiKey(null);
      setSnackbar({
        open: true,
        message: 'API key deleted successfully',
        severity: 'success'
      });
    } catch (err) {
      console.error('Error deleting API key:', err);
      setSnackbar({
        open: true,
        message: 'Failed to delete API key',
        severity: 'error'
      });
    }
  };

  const toggleApiKeyVisibility = (keyId) => {
    setShowApiKeyValue(prev => ({
      ...prev,
      [keyId]: !prev[keyId]
    }));
  };

  const handleCloseSnackbar = () => {
    setSnackbar(prev => ({ ...prev, open: false }));
  };

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
        <Typography variant="h4">Settings</Typography>
        <Button
          variant="contained"
          startIcon={saving ? <CircularProgress size={20} /> : <SaveIcon />}
          onClick={handleSaveSettings}
          disabled={saving}
        >
          Save Changes
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* General Settings */}
        <Grid item xs={12}>
          <Accordion defaultExpanded>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <PaletteIcon sx={{ mr: 1 }} />
                <Typography variant="h6">General Settings</Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={3}>
                <Grid item xs={12} md={4}>
                  <FormControl fullWidth>
                    <InputLabel>Theme</InputLabel>
                    <Select
                      value={userSettings.theme}
                      onChange={(e) => handleDirectSettingChange('theme', e.target.value)}
                      label="Theme"
                    >
                      {themes.map((theme) => (
                        <MenuItem key={theme.value} value={theme.value}>
                          {theme.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={4}>
                  <FormControl fullWidth>
                    <InputLabel>Language</InputLabel>
                    <Select
                      value={userSettings.language}
                      onChange={(e) => handleDirectSettingChange('language', e.target.value)}
                      label="Language"
                    >
                      {languages.map((lang) => (
                        <MenuItem key={lang.value} value={lang.value}>
                          {lang.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={4}>
                  <FormControl fullWidth>
                    <InputLabel>Timezone</InputLabel>
                    <Select
                      value={userSettings.timezone}
                      onChange={(e) => handleDirectSettingChange('timezone', e.target.value)}
                      label="Timezone"
                    >
                      {timezones.map((tz) => (
                        <MenuItem key={tz.value} value={tz.value}>
                          {tz.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
        </Grid>

        {/* Display Settings */}
        <Grid item xs={12}>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <LanguageIcon sx={{ mr: 1 }} />
                <Typography variant="h6">Display Settings</Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={3}>
                <Grid item xs={12} md={4}>
                  <FormControl fullWidth>
                    <InputLabel>Date Format</InputLabel>
                    <Select
                      value={userSettings.display?.dateFormat || 'MM/DD/YYYY'}
                      onChange={(e) => handleUserSettingChange('display', 'dateFormat', e.target.value)}
                      label="Date Format"
                    >
                      {dateFormats.map((format) => (
                        <MenuItem key={format.value} value={format.value}>
                          {format.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={4}>
                  <FormControl fullWidth>
                    <InputLabel>Time Format</InputLabel>
                    <Select
                      value={userSettings.display?.timeFormat || '12h'}
                      onChange={(e) => handleUserSettingChange('display', 'timeFormat', e.target.value)}
                      label="Time Format"
                    >
                      <MenuItem value="12h">12 Hour</MenuItem>
                      <MenuItem value="24h">24 Hour</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={4}>
                  <FormControl fullWidth>
                    <InputLabel>Currency</InputLabel>
                    <Select
                      value={userSettings.display?.currency || 'USD'}
                      onChange={(e) => handleUserSettingChange('display', 'currency', e.target.value)}
                      label="Currency"
                    >
                      {currencies.map((currency) => (
                        <MenuItem key={currency.value} value={currency.value}>
                          {currency.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
        </Grid>

        {/* Notification Settings */}
        <Grid item xs={12}>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <NotificationsIcon sx={{ mr: 1 }} />
                <Typography variant="h6">Notification Settings</Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={userSettings.notifications?.email || false}
                        onChange={(e) => handleUserSettingChange('notifications', 'email', e.target.checked)}
                      />
                    }
                    label="Email Notifications"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={userSettings.notifications?.push || false}
                        onChange={(e) => handleUserSettingChange('notifications', 'push', e.target.checked)}
                      />
                    }
                    label="Push Notifications"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={userSettings.notifications?.predictions || false}
                        onChange={(e) => handleUserSettingChange('notifications', 'predictions', e.target.checked)}
                      />
                    }
                    label="Prediction Updates"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={userSettings.notifications?.reports || false}
                        onChange={(e) => handleUserSettingChange('notifications', 'reports', e.target.checked)}
                      />
                    }
                    label="Report Notifications"
                  />
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
        </Grid>

        {/* Astrology Settings */}
        <Grid item xs={12}>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <SecurityIcon sx={{ mr: 1 }} />
                <Typography variant="h6">Astrology Settings</Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>House System</InputLabel>
                    <Select
                      value={userSettings.astrology?.houseSystem || 'placidus'}
                      onChange={(e) => handleUserSettingChange('astrology', 'houseSystem', e.target.value)}
                      label="House System"
                    >
                      {houseSystems.map((system) => (
                        <MenuItem key={system.value} value={system.value}>
                          {system.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Box>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={userSettings.astrology?.showRetrogrades || false}
                          onChange={(e) => handleUserSettingChange('astrology', 'showRetrogrades', e.target.checked)}
                        />
                      }
                      label="Show Retrograde Indicators"
                    />
                    <FormControlLabel
                      control={
                        <Switch
                          checked={userSettings.astrology?.showArabicParts || false}
                          onChange={(e) => handleUserSettingChange('astrology', 'showArabicParts', e.target.checked)}
                        />
                      }
                      label="Show Arabic Parts"
                    />
                  </Box>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle1" gutterBottom>
                    Aspect Orbs (degrees)
                  </Typography>
                  <Grid container spacing={2}>
                    {Object.entries(userSettings.astrology?.aspectOrbs || {}).map(([aspect, orb]) => (
                      <Grid item xs={6} md={2.4} key={aspect}>
                        <TextField
                          label={aspect.charAt(0).toUpperCase() + aspect.slice(1)}
                          type="number"
                          value={orb}
                          onChange={(e) => handleAspectOrbChange(aspect, e.target.value)}
                          inputProps={{ min: 0, max: 15, step: 0.5 }}
                          fullWidth
                          size="small"
                        />
                      </Grid>
                    ))}
                  </Grid>
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
        </Grid>

        {/* Privacy Settings */}
        <Grid item xs={12}>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <SecurityIcon sx={{ mr: 1 }} />
                <Typography variant="h6">Privacy Settings</Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <Grid item xs={12} md={4}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={userSettings.privacy?.shareData || false}
                        onChange={(e) => handleUserSettingChange('privacy', 'shareData', e.target.checked)}
                      />
                    }
                    label="Share Anonymous Data"
                  />
                </Grid>
                <Grid item xs={12} md={4}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={userSettings.privacy?.analytics || false}
                        onChange={(e) => handleUserSettingChange('privacy', 'analytics', e.target.checked)}
                      />
                    }
                    label="Analytics Tracking"
                  />
                </Grid>
                <Grid item xs={12} md={4}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={userSettings.privacy?.marketing || false}
                        onChange={(e) => handleUserSettingChange('privacy', 'marketing', e.target.checked)}
                      />
                    }
                    label="Marketing Communications"
                  />
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
        </Grid>

        {/* API Keys Management */}
        <Grid item xs={12}>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <ApiIcon sx={{ mr: 1 }} />
                <Typography variant="h6">API Keys</Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Box sx={{ mb: 2 }}>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => setShowApiKeyDialog(true)}
                >
                  Create New API Key
                </Button>
              </Box>
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Name</TableCell>
                      <TableCell>Description</TableCell>
                      <TableCell>Key</TableCell>
                      <TableCell>Created</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {apiKeys.map((apiKey) => (
                      <TableRow key={apiKey.id}>
                        <TableCell>{apiKey.name}</TableCell>
                        <TableCell>{apiKey.description}</TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Typography variant="body2" sx={{ fontFamily: 'monospace', mr: 1 }}>
                              {showApiKeyValue[apiKey.id] ? apiKey.key : '••••••••••••••••'}
                            </Typography>
                            <IconButton
                              size="small"
                              onClick={() => toggleApiKeyVisibility(apiKey.id)}
                            >
                              {showApiKeyValue[apiKey.id] ? <VisibilityOffIcon /> : <VisibilityIcon />}
                            </IconButton>
                          </Box>
                        </TableCell>
                        <TableCell>
                          {new Date(apiKey.createdAt).toLocaleDateString()}
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={apiKey.status}
                            color={apiKey.status === 'active' ? 'success' : 'error'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <IconButton
                            color="error"
                            onClick={() => {
                              setSelectedApiKey(apiKey);
                              setShowDeleteDialog(true);
                            }}
                            size="small"
                          >
                            <DeleteIcon />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </AccordionDetails>
          </Accordion>
        </Grid>
      </Grid>

      {/* Create API Key Dialog */}
      <Dialog open={showApiKeyDialog} onClose={() => setShowApiKeyDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New API Key</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                label="Name"
                fullWidth
                value={newApiKey.name}
                onChange={(e) => setNewApiKey(prev => ({ ...prev, name: e.target.value }))}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Description"
                fullWidth
                multiline
                rows={3}
                value={newApiKey.description}
                onChange={(e) => setNewApiKey(prev => ({ ...prev, description: e.target.value }))}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowApiKeyDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateApiKey} variant="contained">
            Create
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete API Key Dialog */}
      <Dialog open={showDeleteDialog} onClose={() => setShowDeleteDialog(false)}>
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete the API key "{selectedApiKey?.name}"?
            This action cannot be undone and will immediately revoke access.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowDeleteDialog(false)}>Cancel</Button>
          <Button onClick={handleDeleteApiKey} color="error" variant="contained">
            Delete
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

export default Settings;