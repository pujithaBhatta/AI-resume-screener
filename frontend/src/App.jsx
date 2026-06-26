/**
 * App.jsx - Main Application Component
 * =======================================
 * Sets up routing so different URLs show different pages.
 * 
 * REACT ROUTER CONCEPTS:
 * - <BrowserRouter>: Enables URL-based navigation
 * - <Routes>: Container for all route definitions  
 * - <Route path="/x" element={<Component/>}>: Maps URL to component
 * - <Navigate to="/x">: Redirects to another URL
 * - ProtectedRoute: Custom component that redirects to login if not authenticated
 */

import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './hooks/useAuth';

// Pages
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import JobsPage from './pages/JobsPage';
import ResumesPage from './pages/ResumesPage';
import UploadPage from './pages/UploadPage';
import RankingsPage from './pages/RankingsPage';
import ResumeDetailPage from './pages/ResumeDetailPage';

// Layout
import Layout from './components/layout/Layout';

// ProtectedRoute: Redirects to /login if user is not authenticated
function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <AuthProvider>
      {/* Toast notification container */}
      <Toaster position="top-right" toastOptions={{
        duration: 3000,
        style: { borderRadius: '10px', fontSize: '14px' }
      }} />
      
      <BrowserRouter>
        <Routes>
          {/* Public route */}
          <Route path="/login" element={<LoginPage />} />
          
          {/* Protected routes — require login */}
          <Route path="/" element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="jobs" element={<JobsPage />} />
            <Route path="resumes" element={<ResumesPage />} />
            <Route path="resumes/:id" element={<ResumeDetailPage />} />
            <Route path="upload" element={<UploadPage />} />
            <Route path="rankings/:jobId" element={<RankingsPage />} />
          </Route>
          
          {/* Catch-all: redirect unknown URLs to dashboard */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
