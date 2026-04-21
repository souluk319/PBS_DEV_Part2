declare global {
  var __PBS_OPS_API_BASE_URL__: string | undefined;
}

const DEFAULT_OPS_API_BASE_URL = 'http://127.0.0.1:8000';

function trimTrailingSlash(value: string): string {
  return value.replace(/\/+$/, '');
}

export function setOpsApiBaseUrl(value?: string | null) {
  const normalized = value?.trim();
  globalThis.__PBS_OPS_API_BASE_URL__ = normalized ? trimTrailingSlash(normalized) : undefined;
}

export function getOpsApiBaseUrl(): string {
  const runtimeValue = globalThis.__PBS_OPS_API_BASE_URL__;
  if (runtimeValue) {
    return runtimeValue;
  }

  const envValue = import.meta.env.VITE_OPS_API_BASE_URL?.trim();
  if (envValue) {
    return trimTrailingSlash(envValue);
  }

  return DEFAULT_OPS_API_BASE_URL;
}
