import {
  createApi,
  BaseQueryFn,
  FetchArgs,
  fetchBaseQuery
} from '@reduxjs/toolkit/query/react';

// Import types from the main RTK package
import type {
  SerializedError
} from '@reduxjs/toolkit';

// Define FetchBaseQueryError type locally since it's not exported
export interface FetchBaseQueryError {
  status: number;
  data: any;
}

// Define EndpointBuilder type locally
export type EndpointBuilder<
  BaseQuery extends BaseQueryFn,
  TagTypes extends string,
  ReducerPath extends string
> = {
  query: <ResultType = unknown, QueryArg = void>(
    definition: {
      query: (arg: QueryArg) => string | FetchArgs;
      transformResponse?: (response: any, meta: any, arg: QueryArg) => ResultType;
      providesTags?: TagTypes[] | ((result: ResultType | undefined, error: FetchBaseQueryError | SerializedError | undefined, arg: QueryArg) => TagTypes[]);
    }
  ) => any;
  mutation: <ResultType = unknown, QueryArg = void>(
    definition: {
      query: (arg: QueryArg) => string | FetchArgs;
      transformResponse?: (response: any, meta: any, arg: QueryArg) => ResultType;
      invalidatesTags?: TagTypes[] | ((result: ResultType | undefined, error: FetchBaseQueryError | SerializedError | undefined, arg: QueryArg) => TagTypes[]);
    }
  ) => any;
};

// Define custom tagged types for the API
export type ApiTags = 'Chart' | 'User' | 'Dashboard';

// Define a type for API endpoints
export type ApiEndpoint<ResultType, QueryArg = void> = {
  query: (arg: QueryArg) => string | FetchArgs;
  providesTags?: ApiTags[];
  invalidatesTags?: ApiTags[];
};

// Define the builder type
export type ApiEndpointBuilder = EndpointBuilder<
  BaseQueryFn<string | FetchArgs, unknown, FetchBaseQueryError>,
  ApiTags,
  'api'
>;

export interface ApiError {
  status: number;
  message: string;
  details?: Record<string, string[]>;
}

// API Response wrapper type
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface ApiListResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  message?: string;
  status: 'success' | 'error';
}

export interface PaginationParams {
  page?: number;
  pageSize?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

// Common query parameters
export interface DateRangeParams {
  startDate: string;
  endDate: string;
}

export interface LocationParams {
  latitude: number;
  longitude: number;
}

export interface TimingParams extends DateRangeParams {
  technique: string;
}

// Helper types for RTK Query
export type QueryDefinition<QueryArg, BaseQuery, TagTypes, ResultType> = {
  query: (arg: QueryArg) => string | FetchArgs;
  transformResponse?: (response: any) => ResultType;
  providesTags?: TagTypes[] | ((result: ResultType, error: any, arg: QueryArg) => TagTypes[]);
};

export type MutationDefinition<QueryArg, BaseQuery, TagTypes, ResultType> = {
  query: (arg: QueryArg) => string | FetchArgs;
  transformResponse?: (response: any) => ResultType;
  invalidatesTags?: TagTypes[] | ((result: ResultType, error: any, arg: QueryArg) => TagTypes[]);
};

// User types
export interface User {
  id: string;
  email: string;
  username: string;
  firstName?: string;
  lastName?: string;
  birthDate?: string;
  birthTime?: string;
  birthPlace?: string;
  settings?: UserSettings;
}

export interface UserSettings {
  theme: 'light' | 'dark';
  houseSystem: 'placidus' | 'whole-sign' | 'equal';
  aspectOrbs: 'strict' | 'medium' | 'loose';
}

// Astrological types
export interface BirthChart {
  planets: PlanetPosition[];
  houses: HousePosition[];
  angles: Angle[];
  aspects: Aspect[];
}

export interface BirthChartParams {
  date: string;
  time: string;
  latitude: number;
  longitude: number;
}

export interface PlanetPosition {
  planet: string;
  sign: string;
  degree: number;
  speed: number;
  house: number;
}

export interface HousePosition {
  house: number;
  sign: string;
  degree: number;
}

export interface Angle {
  name: string;
  sign: string;
  degree: number;
}

export interface Aspect {
  planet1: string;
  planet2: string;
  aspect: string;
  orb: number;
}

export interface Transit {
  planet: string;
  sign: string;
  degree: number;
  aspect?: string;
  aspectedPlanet?: string;
}

export interface MoonInfo {
  phase: string;
  sign: string;
  illumination: number;
}

export interface StarPosition {
  name: string;
  constellation: string;
  rightAscension: number;
  declination: number;
  magnitude: number;
}

export interface PlanetaryDignity {
  planet: string;
  sign: string;
  dignity: string;
  score: number;
}

export interface PlanetaryDignitiesParams {
  planets: string[];
  date: string;
}

export interface VisibleStarsParams {
  date: string;
  time: string;
  latitude: number;
  longitude: number;
  magnitude?: number;
}

export interface AstrologicalChart {
  id: string;
  name: string;
  type: 'natal' | 'transit' | 'synastry' | 'composite';
  data: BirthChart;
  date: string;
  location: string;
  notes?: string;
}

// Additional types for new features
export interface NatalDataRequest {
  birthDate: string;
  birthTime: string;
  latitude: number;
  longitude: number;
}

export interface AntisciaResponse {
  antisciaPoints: PlanetPosition[];
  contraAntisciaPoints: PlanetPosition[];
}

export interface ArabicPartsResponse {
  parts: ArabicPart[];
}

export interface ArabicPart {
  name: string;
  degree: number;
  sign: string;
  formula: string;
}

export interface DashboardSummaryResponse {
  currentTransits: Transit[];
  moonPhase: MoonInfo;
  activeAspects: Aspect[];
  predictions: Prediction[];
}

export interface Prediction {
  type: string;
  description: string;
  startDate: string;
  endDate: string;
  intensity: number;
}

export interface InterpretationRequest {
  chart: BirthChart;
  type: 'natal' | 'transit' | 'synastry';
  focus?: string[];
}

export interface InterpretationResponse {
  interpretations: Interpretation[];
}

export interface Interpretation {
  topic: string;
  description: string;
  strength: number;
}