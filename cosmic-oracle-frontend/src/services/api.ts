import { createApi, fetchBaseQuery, BaseQueryFn, FetchArgs, FetchBaseQueryError } from '@reduxjs/toolkit/query/react';
import type { Headers } from '@reduxjs/toolkit/query/react';
import type { RootState } from '../store';
import { 
  User,
  BirthChart,
  Transit,
  MoonInfo,
  StarPosition,
  PlanetaryDignity,
  AstrologicalChart,
  BirthChartParams,
  VisibleStarsParams,
  PlanetaryDignitiesParams,
  ApiResponse,
  NatalDataRequest,
  AntisciaResponse,
  ArabicPartsResponse,
  DashboardSummaryResponse,
  InterpretationRequest,
  InterpretationResponse
} from '../types/apiTypes';

// Configuration
const API_URL = process.env.REACT_APP_API_URL as string;
const API_KEY = process.env.REACT_APP_API_KEY as string;

// Validate environment variables at runtime
if (!API_URL || !API_KEY) {
  throw new Error('Missing required environment variables: REACT_APP_API_URL and REACT_APP_API_KEY must be set');
}

// Define response types for strict typing
interface BaseResponse {
  success: boolean;
  message?: string;
  data?: unknown;
}

interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

// Define parameter types with proper typing
interface VisibleStarsParams {
  latitude: number;
  longitude: number;
}

interface PlanetaryDignitiesParams {
  date: string;
  time: string;
}

interface ChartIdParam {
  chartId: string;
}

interface TimingParams extends ChartIdParam {
  technique: string;
}

interface DateRangeParams {
  startDate: string;
  endDate: string;
}

interface YearParam {
  year: number;
}

export interface BirthChartParams {
  date: string;
  time: string;
  latitude: number;
  longitude: number;
}

// --- NEW/UPDATED TYPES FOR NEW ENDPOINTS ---
export interface NatalDataRequest {
  date: string;
  time: string;
  latitude: number;
  longitude: number;
  timezone?: string;
  locationName?: string;
}

export interface AntisciaResponse {
  planetPositions: {
    [key: string]: {
      longitude: number;
      antisciaLongitude: number;
      contraAntisciaLongitude: number;
    };
  };
}

export interface ArabicPartsResponse {
  parts: Array<{
    name: string;
    longitude: number;
  }>;
}

export interface InterpretationRequest {
  chartData: any;
  query: string;
  scope?: 'natal' | 'transit' | 'predictive';
}

export interface InterpretationResponse {
  interpretation: string;
  keywords?: string[];
  confidenceScore?: number;
}

// Model types
export interface User {
  id: string;
  email: string;
  birthDate: string;
  birthTime: string;
  birthLocation: string;
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

export enum Dignity {
  RULERSHIP = 'RULERSHIP',
  EXALTATION = 'EXALTATION',
  TRIPLICITY = 'TRIPLICITY',
  TERM = 'TERM',
  FACE = 'FACE',
  DETRIMENT = 'DETRIMENT',
  FALL = 'FALL',
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
  aiPowered: boolean;
}

export interface StarPosition {
  name: string;
  ra: number;
  dec: number;
  magnitude: number;
  constellation: string;
}

export interface DignityScore {
  score: number;// Tag types for caching
type TagTypes = 'User' | 'Chart' | 'Dashboard';

// Get environment-specific API URL and key
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';
const API_KEY = process.env.REACT_APP_API_KEY || '';

// Base query with proper TypeScript typing
const baseQuery = fetchBaseQuery({
  baseUrl: API_URL,
  credentials: 'include',
  prepareHeaders: (headers, { getState }) => {
    const state = getState() as RootState;
    const token = state.auth?.token;

    // Add API key and auth token if available
    headers.set('X-API-Key', API_KEY);
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }
    
    headers.set('Content-Type', 'application/json');
    return headers;
  },
});
  return result;
};

export const api = createApi({
  reducerPath: 'api',
  baseQuery,  baseQuery,
  tagTypes: ['User', 'Chart', 'Dashboard'] as const,
  endpoints: (build) => ({
    // User endpoints
    getCurrentUser: build.query<User, void>({
      query: () => ({
        url: 'users/me'
      }),
      providesTags: ['User']
    }),

    updateUser: build.mutation<User, Partial<User>>({
      query: (update) => ({
        url: 'users/me',
        method: 'PATCH',
        body: update
      }),
      invalidatesTags: ['User']
    }),

    // Chart endpoints
    getBirthChart: build.query<BirthChart, BirthChartParams>({
      query: (params) => ({
        url: 'astronomical/birth-chart',
        params
      }),
      providesTags: ['Chart']
    }),

    getCurrentTransits: build.query<Transit[], void>({
      query: () => ({
        url: 'astronomical/current-transits'
      }),
      providesTags: ['Chart']
    }),

    getMoonInfo: build.query<MoonInfo, void>({
      query: () => ({
        url: 'astronomical/moon-info'
      }),
      providesTags: ['Chart']
    }),

    getVisibleStars: build.query<StarPosition[], VisibleStarsParams>({
      query: (params) => ({
        url: 'astronomical/visible-stars',
        params
      }),
      providesTags: ['Chart']
    }),

    getPlanetaryDignities: build.query<PlanetaryDignity[], PlanetaryDignitiesParams>({
      query: (params) => ({
        url: 'astronomical/dignities',
        params
      }),
      providesTags: ['Chart']
    }),

    // Dashboard endpoints
    getSavedChart: builder.query<ApiResponse<AstrologicalChart>, string>({
      query: (chartId: string) => `charts/${chartId}`,
      providesTags: (_result, _error, id: string) => [{ type: 'Chart' as const, id }],
    }),

    saveChart: builder.mutation<ApiResponse<AstrologicalChart>, Partial<AstrologicalChart>>({
      query: (chart: Partial<AstrologicalChart>) => ({
        url: 'charts',
        method: 'POST',
        body: chart,
      }),
      invalidatesTags: ['Chart'],
    }),

    // New endpoints
    getAntiscia: builder.mutation<ApiResponse<AntisciaResponse>, NatalDataRequest>({
      query: (natalData: NatalDataRequest) => ({
        url: 'astronomical/antiscia',
        method: 'POST',
        body: natalData,
      }),
    }),

    getArabicParts: builder.mutation<ApiResponse<ArabicPartsResponse>, NatalDataRequest>({
      query: (natalData: NatalDataRequest) => ({
        url: 'astronomical/arabic-parts',
        method: 'POST',
        body: natalData,
      }),
    }),

    getDashboardSummary: builder.mutation<ApiResponse<DashboardSummaryResponse>, void>({
      query: () => ({
        url: 'dashboard/summary',
        method: 'POST',
      }),
      invalidatesTags: ['Dashboard'],
    }),

    getAstrologicalInterpretation: builder.mutation<ApiResponse<InterpretationResponse>, InterpretationRequest>({
      query: (request: InterpretationRequest) => ({
        url: 'ai/interpretation',
        method: 'POST',
        body: request,
      }),
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
  useGetSavedChartQuery,
  useSaveChartMutation,
  // New mutation hooks
  useGetAntisciaMutation,
  useGetArabicPartsMutation,
  useGetDashboardSummaryMutation,
  useGetAstrologicalInterpretationMutation,
} = api;

export default api;