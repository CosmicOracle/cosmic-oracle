declare module '@reduxjs/toolkit/query/react' {
  import { BaseQueryFn } from '@reduxjs/toolkit/query';
  
  export interface EndpointDefinition<QueryArg, ResultType> {
    query: (arg: QueryArg) => string | FetchArgs;
    transformResponse?: (response: unknown) => ResultType;
    providesTags?: string[];
    invalidatesTags?: string[];
  }

  export interface FetchArgs {
    url: string;
    method?: string;
    body?: any;
    params?: any;
    headers?: Record<string, string>;
  }

  export interface BaseQueryApi {
    signal: AbortSignal;
    dispatch: Function;
    getState: () => unknown;
  }

  export type BaseQueryFn<
    Args = any,
    Result = unknown,
    Error = unknown,
    DefinitionExtraOptions = {},
    Meta = {}
  > = (
    args: Args,
    api: BaseQueryApi,
    extraOptions: DefinitionExtraOptions
  ) => Promise<{ data: Result } | { error: Error }>;

  export function fetchBaseQuery(
    options: { baseUrl: string; credentials?: RequestCredentials }
  ): BaseQueryFn;

  export function createApi<
    BaseQuery extends BaseQueryFn,
    Definitions extends { [K: string]: any }
  >(options: {
    baseQuery: BaseQuery;
    endpoints: (build: any) => Definitions;
    reducerPath?: string;
    tagTypes?: string[];
  }): any;
}
