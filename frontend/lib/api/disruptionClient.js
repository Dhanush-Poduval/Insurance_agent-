import axios from 'axios';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const client = axios.create({ baseURL: `${BASE_URL}/api/v1`, timeout: 10000 });

client.interceptors.response.use(
  (res) => res.data,
  (err) => Promise.reject(err.response?.data || err.message)
);

export const disruptionClient = {
  getActiveDisruptions: () => client.get('/disruptions/active'),
  getByArea: (area) => client.get('/disruptions/area', { params: { area } }),
  getHistory: (params) => client.get('/disruptions/history', { params }),
  createDisruption: (data) => client.post('/disruptions', data),
  getWorkerDisruptions: (workerId) => client.get(`/disruptions/worker/${workerId}`),
};
