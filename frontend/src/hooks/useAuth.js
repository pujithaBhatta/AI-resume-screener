/**
 * hooks/useAuth.js - Authentication Context & Hook
 * ==================================================
 * React Context shares state across the entire app without prop drilling.
 * 
 * HOW REACT CONTEXT WORKS:
 * 1. AuthProvider wraps the whole app and holds auth state
 * 2. Any component can call useAuth() to get/set auth state
 * 3. When state changes, all components using useAuth() re-render
 */

import React, { createContext, useContext, useState, useCallback } from 'react';
import { authAPI } from '../utils/api';
import toast from 'react-hot-toast';

// Create the context
const AuthContext = createContext(null);

// Provider component — wraps the app in App.jsx
export function AuthProvider({ children }) {
  // Initialize state from localStorage (persists across page refreshes)
  const [user, setUser] = useState(() => {
    try {
      const saved = localStorage.getItem('user');
      return saved ? JSON.parse(saved) : null;
    } catch { return null; }
  });

  const login = useCallback(async (username, password) => {
    const response = await authAPI.login(username, password);
    const { access_token, username: uname, role } = response.data;
    
    // Store token and user info
    localStorage.setItem('access_token', access_token);
    const userData = { username: uname, role };
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);
    
    toast.success(`Welcome back, ${uname}!`);
    return userData;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    setUser(null);
    toast.success('Logged out successfully');
  }, []);

  return (
    <AuthContext.Provider value={{ user, login, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
}

// Custom hook — use this in any component
export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
