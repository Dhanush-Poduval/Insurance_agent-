import { create } from 'zustand';

export const useDisruptionStore = create((set) => ({
  events: [],
  activeDisruptions: [],
  selectedEvent: null,
  loading: false,
  error: null,

  setEvents: (events) => set({ events }),
  setActiveDisruptions: (activeDisruptions) => set({ activeDisruptions }),
  setSelectedEvent: (selectedEvent) => set({ selectedEvent }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  addEvent: (event) => set((state) => ({ events: [event, ...state.events] })),
  updateEvent: (id, updates) =>
    set((state) => ({
      events: state.events.map((e) => (e.id === id ? { ...e, ...updates } : e)),
      activeDisruptions: state.activeDisruptions.map((e) =>
        e.id === id ? { ...e, ...updates } : e
      ),
    })),
  dismissDisruption: (id) =>
    set((state) => ({
      activeDisruptions: state.activeDisruptions.filter((e) => e.id !== id),
    })),
}));
