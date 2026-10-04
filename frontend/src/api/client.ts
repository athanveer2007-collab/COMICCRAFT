/**
 * API client configuration and health query.
 */

export interface HealthData {
  status: string;
  version: string;
  environment: string;
  storage_writable: boolean;
}

export async function fetchHealth(): Promise<HealthData> {
  const response = await fetch("/api/v1/health");
  if (!response.ok) {
    throw new Error(`Health check failed with status: ${response.status}`);
  }
  return response.json();
}
