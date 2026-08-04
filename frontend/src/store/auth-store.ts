import { create } from "zustand";
import { persist } from "zustand/middleware";
import { decodeAccessToken, type AccessTokenClaims } from "@/lib/jwt";

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  claims: AccessTokenClaims | null;
  setTokens: (accessToken: string, refreshToken: string) => void;
  clear: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      refreshToken: null,
      claims: null,
      setTokens: (accessToken, refreshToken) =>
        set({
          accessToken,
          refreshToken,
          claims: decodeAccessToken(accessToken),
        }),
      clear: () => set({ accessToken: null, refreshToken: null, claims: null }),
    }),
    { name: "siamo-auth" },
  ),
);
