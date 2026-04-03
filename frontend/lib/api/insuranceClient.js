import axios from 'axios';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const client = axios.create({ baseURL: `${BASE_URL}/api/v1`, timeout: 10000 });

client.interceptors.response.use(
  (res) => res.data,
  (err) => Promise.reject(err.response?.data || err.message)
);

export const insuranceClient = {
  getCoverage: (workerId) => client.get(`/coverage/${workerId}`),
  calculatePremium: (params) => client.post('/coverage/calculate-premium', params),
  activateCoverage: (workerId, data) => client.post(`/coverage/${workerId}/activate`, data),
  deactivateCoverage: (workerId) => client.post(`/coverage/${workerId}/deactivate`),
  getCoverageHistory: (workerId) => client.get(`/coverage/${workerId}/history`),
};
