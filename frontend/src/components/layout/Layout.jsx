/**
 * components/layout/Layout.jsx
 * Sidebar + topbar shell that wraps all protected pages.
 * <Outlet /> is where child route content renders.
 */

import React, { useState } from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import {
  LayoutDashboard, Briefcase, FileText, Upload,
  BarChart3, LogOut, Menu, X, Bot, ChevronRight
} from 'lucide-react';

const navItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/jobs',      icon: Briefcase,       label: 'Job Descriptions' },
  { to: '/resumes',   icon: FileText,        label: 'Resumes' },
  { to: '/upload',    icon: Upload,          label: 'Upload Resumes' },
];

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = () => { logout(); navigate('/login'); };

  const SidebarContent = () => (
    <div className="flex flex-col h-full">
      {/* Logo */}
      <div className="flex items-center gap-3 px-6 py-5 border-b border-primary-700">
        <div className="w-9 h-9 bg-white rounded-xl flex items-center justify-center shadow">
          <Bot className="w-5 h-5 text-primary-600" />
        </div>
        <div>
          <div className="text-white font-bold text-sm leading-tight">AI Resume</div>
          <div className="text-primary-300 text-xs">Screener Pro</div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink key={to} to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all group ${
                isActive
                  ? 'bg-white text-primary-700 shadow-sm'
                  : 'text-primary-100 hover:bg-primary-700 hover:text-white'
              }`
            }
            onClick={() => setSidebarOpen(false)}
          >
            <Icon className="w-4 h-4 flex-shrink-0" />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* User */}
      <div className="px-3 py-4 border-t border-primary-700">
        <div className="flex items-center gap-3 px-3 py-2 rounded-lg mb-2">
          <div className="w-8 h-8 bg-primary-400 rounded-full flex items-center justify-center">
            <span className="text-white text-xs font-bold">
              {user?.username?.[0]?.toUpperCase()}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-white text-sm font-medium truncate">{user?.username}</div>
            <div className="text-primary-300 text-xs capitalize">{user?.role}</div>
          </div>
        </div>
        <button onClick={handleLogout}
          className="flex items-center gap-2 w-full px-3 py-2 text-primary-200 hover:text-white hover:bg-primary-700 rounded-lg text-sm transition-colors">
          <LogOut className="w-4 h-4" />
          Sign out
        </button>
      </div>
    </div>
  );

  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden">
      {/* Desktop sidebar */}
      <aside className="hidden lg:flex flex-col w-60 bg-primary-800 flex-shrink-0">
        <SidebarContent />
      </aside>

      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div className="lg:hidden fixed inset-0 z-50 flex">
          <div className="w-60 bg-primary-800 flex flex-col">
            <SidebarContent />
          </div>
          <div className="flex-1 bg-black/40" onClick={() => setSidebarOpen(false)} />
        </div>
      )}

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Topbar */}
        <header className="bg-white border-b border-gray-200 px-4 lg:px-6 py-3 flex items-center gap-3 flex-shrink-0">
          <button onClick={() => setSidebarOpen(true)}
            className="lg:hidden p-1.5 rounded-lg hover:bg-gray-100">
            <Menu className="w-5 h-5 text-gray-500" />
          </button>
          <div className="flex-1" />
          <div className="text-sm text-gray-500">
            AI Resume Screener
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-auto p-4 lg:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
