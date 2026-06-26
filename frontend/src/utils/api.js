/**
 * utils/api.js - Axios API Client
 * ==================================
 * Central place for all HTTP requests to the backend.
 * 
 * HOW IT WORKS:
 * - axios.create() makes a configured HTTP client
 * - Interceptors automatically add the JWT token to every request
 * - If a 401 (Unauthorized) response comes back, we log the user out
 */

import axios from 'axios';

// Base URL for all API calls
// In development, package.json "proxy" forwards /api/* to localhost:8000
const API_BASE = process.env.REACT_APP_API_URL || '';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,  // 30 second timeout
});

// ---- Request Interceptor ----
// Runs BEFORE every request is sent
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      // Add JWT token to Authorization header
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ---- Response Interceptor ----
// Runs AFTER every response is received
api.interceptors.response.use(
  (response) => response,  // Success: pass through
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid — log out
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ============================================================
// Auth API
// ============================================================
export const authAPI = {
  login: (username, password) =>
    api.post('/api/auth/login', { username, password }),
};

// ============================================================
// Jobs API
// ============================================================
export const jobsAPI = {
  list: () => api.get('/api/jobs/'),
  get: (id) => api.get(`/api/jobs/${id}`),
  create: (data) => api.post('/api/jobs/', data),
  delete: (id) => api.delete(`/api/jobs/${id}`),
};

// ============================================================
// Resumes API
// ============================================================
export const resumesAPI = {
  upload: (files, jobId) => {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    if (jobId) formData.append('job_id', jobId);
    return api.post('/api/resumes/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  list: (params) => api.get('/api/resumes/', { params }),
  get: (id) => api.get(`/api/resumes/${id}`),
  delete: (id) => api.delete(`/api/resumes/${id}`),
};

// ============================================================
// Screening API
// ============================================================
export const screeningAPI = {
  score: (jobId, resumeIds) =>
    api.post('/api/screening/score', { job_id: jobId, resume_ids: resumeIds }),
  rankings: (jobId) => api.get(`/api/screening/rankings/${jobId}`),
};

// ============================================================
// Reports API
// ============================================================
export const reportsAPI = {
  downloadPDF: (jobId) =>
    api.get(`/api/reports/pdf/${jobId}`, { responseType: 'blob' }),
  downloadExcel: (jobId) =>
    api.get(`/api/reports/excel/${jobId}`, { responseType: 'blob' }),
};

// ============================================================
// Analytics API
// ============================================================
export const analyticsAPI = {
  stats: () => api.get('/api/analytics/stats'),
  topSkills: () => api.get('/api/analytics/top-skills'),
};

// Helper to trigger file downloads from blob responses
export const downloadBlob = (blob, filename) => {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};

export default api;
