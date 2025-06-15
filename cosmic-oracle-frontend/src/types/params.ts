export interface BaseParams {
  [key: string]: any;
}

export interface ChartParams extends BaseParams {
  date: string;
  time: string;
  latitude?: number;
  longitude?: number;
}
