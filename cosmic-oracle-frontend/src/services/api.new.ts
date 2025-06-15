import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import type { 
  User, BirthChart, Transit, MoonInfo, 
  StarPosition, PlanetaryDignity, AstrologicalChart,
  BirthChartParams, VisibleStarsParams, PlanetaryDignitiesParams
} from '../types';

// Cloud Service Configuration
const API_URL = process.env.REACT_APP_API_URL;
const API_KEY = process.env.REACT_APP_API_KEY;

if (!API_URL || !API_KEY) {
  throw new Error('Missing required environment variables: REACT_APP_API_URL and REACT_APP_API_KEY must be set');
}

const baseQuery = fetchBaseQuery({
  baseUrl: API_URL,
  prepareHeaders: (headers) => {
    headers.set('X-API-Key', API_KEY);
    return headers;
  }
});

export const api = createApi({
  reducerPath: 'api',
  baseQuery,
  tagTypes: ['User', 'Chart', 'Dashboard'] as const,
  endpoints: (builder) => ({
    // User endpoints
    getCurrentUser: builder.query({
      query: () => 'users/me',
      providesTags: ['User']
    }),
    updateUser: builder.mutation({
      query: (update) => ({
        url: 'users/me',
        method: 'PATCH',
        body: update
      }),
      invalidatesTags: ['User']
    }),
    // Chart endpoints
    getBirthChart: builder.query({
      query: (params) => ({
        url: 'astronomical/birth-chart',
        params
      }),
      providesTags: ['Chart']
    }),
    getCurrentTransits: builder.query({
      query: () => 'astronomical/current-transits',
      providesTags: ['Chart']
    }),
    getMoonInfo: builder.query({
      query: () => 'astronomical/moon-info',
      providesTags: ['Chart']
    }),
    getVisibleStars: builder.query({
      query: (params) => ({
        url: 'astronomical/visible-stars',
        params
      }),
      providesTags: ['Chart']
    }),
    getPlanetaryDignities: builder.query({
      query: (params) => ({
        url: 'astronomical/dignities',
        params
      }),
      providesTags: ['Chart']
    }),
    getSavedChart: builder.query({
      query: (chartId) => `charts/${chartId}`,
      providesTags: (_result, _error, id) => [{ type: 'Chart', id }]
    }),
    saveChart: builder.mutation({
      query: (chart) => ({
        url: 'charts',
        method: 'POST',
        body: chart
      }),
      invalidatesTags: ['Chart']
    })
  })
});

export const {
  useGetCurrentUserQuery,
  useUpdateUserMutation,
  useGetBirthChartQuery,
  useGetCurrentTransitsQuery,
  useGetMoonInfoQuery,
  useGetVisibleStarsQuery,
  useGetPlanetaryDignitiesQuery,
  useGetSavedChartQuery,
  useSaveChartMutation
} = api;
