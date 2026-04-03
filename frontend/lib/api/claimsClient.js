import axios from 'axios';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const client = axios.create({ baseURL: `${BASE_URL}/api/v1`, timeout: 10000 });

client.interceptors.response.use(
  (res) => res.data,
  (err) => Promise.reject(err.response?.data || err.message)
);

export const claimsClient = {
  submitClaim: (data) => client.post('/claims', data),
  getWorkerClaims: (workerId, params) => client.get(`/claims/worker/${workerId}`, { params }),
  getClaim: (claimId) => client.get(`/claims/${claimId}`),
  updateClaimStatus: (claimId, status) => client.patch(`/claims/${claimId}/status`, { status }),
  getPendingClaims: () => client.get('/claims/pending'),
};
