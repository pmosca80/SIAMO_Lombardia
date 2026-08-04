import axios, { AxiosError, type InternalAxiosRequestConfig } from "axios";
import { apiBaseUrl } from "@/lib/config";
import { useAuthStore } from "@/store/auth-store";
import type { TokenPair } from "@/types/api";

export const api = axios.create({ baseURL: apiBaseUrl });

api.interceptors.request.use((config) => {
  const { accessToken } = useAuthStore.getState();
  if (accessToken) {
    config.headers.set("Authorization", `Bearer ${accessToken}`);
  }
  return config;
});

// Le richieste che arrivano mentre un refresh è in corso attendono la
// stessa promise invece di scatenare ciascuna il proprio /auth/refresh
// (il refresh token è a uso singolo: un secondo refresh in parallelo lo
// invaliderebbe, vedi AuthService.refresh sul backend).
let refreshPromise: Promise<string> | null = null;

async function refreshAccessToken(): Promise<string> {
  const { refreshToken, setTokens, clear } = useAuthStore.getState();
  if (!refreshToken) {
    clear();
    throw new Error("Nessun refresh token disponibile.");
  }
  try {
    const { data } = await axios.post<TokenPair>(`${apiBaseUrl}/auth/refresh`, {
      refresh_token: refreshToken,
    });
    setTokens(data.access_token, data.refresh_token);
    return data.access_token;
  } catch (err) {
    clear();
    throw err;
  }
}

interface RetriableConfig extends InternalAxiosRequestConfig {
  _retried?: boolean;
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const config = error.config as RetriableConfig | undefined;
    const isAuthRoute = config?.url?.startsWith("/auth/");

    if (error.response?.status !== 401 || !config || config._retried || isAuthRoute) {
      throw error;
    }
    config._retried = true;

    refreshPromise ??= refreshAccessToken().finally(() => {
      refreshPromise = null;
    });
    const accessToken = await refreshPromise;
    config.headers.set("Authorization", `Bearer ${accessToken}`);
    return api(config);
  },
);
