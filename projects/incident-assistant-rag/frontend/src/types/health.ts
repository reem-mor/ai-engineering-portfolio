export type HealthResponse = {
  status: string;
  service: string;
  version: string;
  environment: string;
  database_enabled: boolean;
};
