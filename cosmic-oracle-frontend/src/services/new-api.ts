import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

const BASE_URL = 'http://localhost:8000/api';

// Query parameter types
interface QueryParams {
  date?: string;
  time?: string;
  latitude?: number;
  longitude?: number;
  startDate?: string;
  endDate?: string;
  chartId?: string;
  technique?: string;
  year?: number;
}

// Define response types
interface BaseResponse<T> {
  success: boolean;
  message?: string;
  data?: T;
}

export interface BirthChart {
  id: string;
  userId: string;
  name: string;
  birthDate: string;
  birthTime: string;
  birthLocation: string;
  timezone: string;
}

export interface MoonInfo {
  phase: string;
  sign: string;
  house: number;
  illumination: number;
  mansion: {
    number: number;
    name: string;
  };
  nextFullMoon: string;
  nextNewMoon: string;
}

export interface TransitAspect {
  to: string;
  type: string;
  orb: number;
}

export interface Transit {
  planet: string;
  sign: string;
  house: number;
  aspects: TransitAspect[];
}

export interface Pattern {
  name: string;
  description: string;
  planets: string[];
}

export interface TimingTechnique {
  name: string;
  description: string;
}

export interface PredictiveEvent {
  startDate: string;
  endDate: string;
  description: string;
  type: string;
  significance: string;
}

export interface User {
  id: string;
  email: string;
  birthDate: string;
  birthTime: string;
  birthLocation: string;
}

export interface AstrologicalChart {
  id: string;
  userId: string;
  type: 'natal' | 'transit' | 'composite';
  data: BirthChart;
  interpretation: string;
  createdAt: string;
}

export interface DashboardSummary {
  title: string;
  summaryText: string;
  dynamicTip: string;
  sourceDateLoaded: boolean;
  aiPowered: boolean;
}

// Create API service
export const api = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({
    baseUrl: BASE_URL,
    credentials: 'include',
    prepareHeaders: (headers: Headers) => {
      const token = localStorage.getItem('token');
      if (token) {
        headers.set('Authorization', `Bearer ${token}`);
      }
      return headers;
    },
  }),
  tagTypes: ['User', 'Chart', 'Dashboard'] as const,
  endpoints: (builder) => ({
    getCurrentUser: builder.query({
      query: () => 'users/me',
      providesTags: ['User'],
    }),
    updateUser: builder.mutation({
      query: (update: Partial<User>) => ({
        url: 'users/me',
        method: 'PATCH',
        body: update,
      }),
      invalidatesTags: ['User'],
    }),
    getBirthChart: builder.query({
      query: (params: { date: string; time: string; latitude: number; longitude: number }) => ({
        url: 'astronomical/birth-chart',
        params,
      }),
    }),
    getCurrentTransits: builder.query({
      query: () => 'astronomical/current-transits',
    }),
    getMoonInfo: builder.query({
      query: () => 'astronomical/moon-info',
    }),
    getVisibleStars: builder.query({
      query: (params: { latitude: number; longitude: number }) => ({
        url: 'astronomical/visible-stars',
        params,
      }),
    }),
    getPlanetaryDignities: builder.query({
      query: (params: { date: string; time: string }) => ({
        url: 'astronomical/dignities',
        params,
      }),
    }),
    getAspectPatterns: builder.query({
      query: ({ chartId }: { chartId: string }) => `astronomical/patterns/${chartId}`,
    }),
    getTimingTechniques: builder.query({
      query: ({ chartId, technique }: { chartId: string; technique: string }) => 
        `predictive/timing/${chartId}/${technique}`,
    }),
    getPredictiveEvents: builder.query({
      query: (params: { startDate: string; endDate: string }) => ({
        url: 'predictive/events',
        params,
      }),
    }),
    getEclipses: builder.query({
      query: ({ year }: { year: number }) => `predictive/eclipses/${year}`,
    }),
    getSavedChart: builder.query({
      query: (chartId: string) => `charts/${chartId}`,
      providesTags: (_result: unknown, _error: unknown, chartId: string) => [{ type: 'Chart', id: chartId }],
    }),
    saveChart: builder.mutation({
      query: (chart: Partial<AstrologicalChart>) => ({
        url: 'charts',
        method: 'POST',
        body: chart,
      }),
      invalidatesTags: ['Chart'],
    }),
    getDashboardSummary: builder.query({
      query: () => 'dashboard/summary',
      providesTags: ['Dashboard'],
    }),
    getChartInterpretation: builder.query({
      query: ({ chartId }: { chartId: string }) => `charts/${chartId}/interpretation`,
    }),
  }),
});

// Export hooks for usage in components
export const {
  useGetCurrentUserQuery,
  useUpdateUserMutation,
  useGetBirthChartQuery,
  useGetCurrentTransitsQuery,
  useGetMoonInfoQuery,
  useGetVisibleStarsQuery,
  useGetPlanetaryDignitiesQuery,
  useGetAspectPatternsQuery,
  useGetTimingTechniquesQuery,
  useGetPredictiveEventsQuery,
  useGetEclipsesQuery,
  useGetSavedChartQuery,
  useSaveChartMutation,
  useGetDashboardSummaryQuery,
  useGetChartInterpretationQuery,
} = api;
