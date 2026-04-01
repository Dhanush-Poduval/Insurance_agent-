import { create } from 'zustand';

export const useAdminStore = create((set) => ({
  payouts: [],
  metrics: null,
  workers: [],
  activeFilters: {},
  loading: false,
  error: null,

  setPayouts: (payouts) => set({ payouts }),
  setMetrics: (metrics) => set({ metrics }),
  setWorkers: (workers) => set({ workers }),
  setActiveFilters: (filters) => set((state) => ({ activeFilters: { ...state.activeFilters, ...filters } })),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  updatePayout: (id, updates) =>
    set((state) => ({
      payouts: state.payouts.map((p) => (p.id === id ? { ...p, ...updates } : p)),
    })),
  approvePayout: (id) =>
    set((state) => ({
      payouts: state.payouts.map((p) => (p.id === id ? { ...p, status: 'approved' } : p)),
    })),
  rejectPayout: (id) =>
    set((state) => ({
      payouts: state.payouts.map((p) => (p.id === id ? { ...p, status: 'rejected' } : p)),
    })),
}));
