import axios from 'axios';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const client = axios.create({ baseURL: `${BASE_URL}/api/v1`, timeout: 10000 });

client.interceptors.response.use(
  (res) => res.data,
  (err) => Promise.reject(err.response?.data || err.message)
);

export const analyticsClient = {
  getMetrics: () => client.get('/analytics/metrics'),
  getClaimsTimeline: (days = 7) => client.get('/analytics/claims-timeline', { params: { days } }),
  getPayoutsTimeline: (days = 30) => client.get('/analytics/payouts-timeline', { params: { days } }),
  getWorkerStats: (workerId) => client.get(`/analytics/workers/${workerId}`),
};
