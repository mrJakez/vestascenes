// utils/runtime-config.ts
let cachedConfig: any = null;

export async function getRuntimeConfig() {
  if (cachedConfig) return cachedConfig;

  const res = await fetch("/api/config");
  if (!res.ok) {
    throw new Error("Fehler beim Laden der Konfiguration");
  }

  const config = await res.json();
  cachedConfig = config;
  return config;
}