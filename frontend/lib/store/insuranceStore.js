import { create } from 'zustand';

export const useInsuranceStore = create((set, get) => ({
  coverage: null,
  claims: [],
  coverageHistory: [],
  loading: false,
  error: null,

  setCoverage: (coverage) => set({ coverage }),
  setClaims: (claims) => set({ claims }),
  setCoverageHistory: (coverageHistory) => set({ coverageHistory }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  addClaim: (claim) => set((state) => ({ claims: [claim, ...state.claims] })),
  updateClaim: (id, updates) =>
    set((state) => ({
      claims: state.claims.map((c) => (c.id === id ? { ...c, ...updates } : c)),
    })),
  reset: () => set({ coverage: null, claims: [], coverageHistory: [], loading: false, error: null }),
}));
