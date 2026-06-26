/**
 * pages/DashboardPage.jsx - Analytics Dashboard
 */

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { analyticsAPI } from '../utils/api';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  PieChart, Pie, Cell, ResponsiveContainer, Legend
} from 'recharts';
import { FileText, Briefcase, CheckCircle, XCircle, Clock, TrendingUp, Upload } from 'lucide-react';

const COLORS = { Selected: '#10b981', Rejected: '#ef4444', Maybe: '#f59e0b' };
const PIE_COLORS = ['#10b981', '#ef4444', '#f59e0b'];

function StatCard({ icon: Icon, label, value, color, sub }) {
  return (
    <div className="card flex items-center gap-4">
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${color}`}>
        <Icon className="w-6 h-6 text-white" />
      </div>
      <div>
        <div className="text-2xl font-bold text-gray-900">{value}</div>
        <div className="text-sm text-gray-500">{label}</div>
        {sub && <div className="text-xs text-gray-400">{sub}</div>}
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([analyticsAPI.stats(), analyticsAPI.topSkills()])
      .then(([s, sk]) => { setStats(s.data); setSkills(sk.data); })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="w-8 h-8 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin" />
    </div>
  );

  const pieData = stats ? [
    { name: 'Selected', value: stats.selected },
    { name: 'Rejected', value: stats.rejected },
    { name: 'Maybe',    value: stats.maybe },
  ] : [];

  return (
    <div className="space-y-6 max-w-6xl">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-500 text-sm mt-0.5">Overview of your screening activity</p>
        </div>
        <Link to="/upload" className="btn-primary flex items-center gap-2">
          <Upload className="w-4 h-4" /> Upload Resumes
        </Link>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={FileText}    label="Total Resumes"   value={stats?.total_resumes || 0} color="bg-primary-600" />
        <StatCard icon={Briefcase}   label="Job Postings"    value={stats?.total_jobs || 0}    color="bg-violet-500" />
        <StatCard icon={CheckCircle} label="Selected"        value={stats?.selected || 0}      color="bg-emerald-500" />
        <StatCard icon={TrendingUp}  label="Avg ATS Score"   value={`${stats?.avg_score || 0}%`} color="bg-amber-500" />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Score Distribution Bar Chart */}
        <div className="card lg:col-span-2">
          <h2 className="font-semibold text-gray-800 mb-4">Score Distribution</h2>
          {stats?.score_distribution?.some(d => d.count > 0) ? (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={stats.score_distribution} barSize={40}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="range" tick={{ fontSize: 12, fill: '#6b7280' }} />
                <YAxis tick={{ fontSize: 12, fill: '#6b7280' }} allowDecimals={false} />
                <Tooltip
                  contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: 13 }}
                  formatter={(v) => [v, 'Candidates']} />
                <Bar dataKey="count" fill="#3b82f6" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-52 flex items-center justify-center text-gray-400 text-sm">
              No screening data yet. <Link to="/upload" className="text-primary-600 ml-1 underline">Upload resumes</Link>
            </div>
          )}
        </div>

        {/* Recommendation Pie Chart */}
        <div className="card">
          <h2 className="font-semibold text-gray-800 mb-4">Recommendations</h2>
          {pieData.some(d => d.value > 0) ? (
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={50} outerRadius={80}
                  paddingAngle={3} dataKey="value">
                  {pieData.map((_, i) => <Cell key={i} fill={PIE_COLORS[i]} />)}
                </Pie>
                <Tooltip formatter={(v, n) => [v, n]} />
                <Legend iconType="circle" iconSize={8}
                  formatter={(v) => <span className="text-xs text-gray-600">{v}</span>} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-52 flex items-center justify-center text-gray-400 text-sm">No data yet</div>
          )}
        </div>
      </div>

      {/* Top Skills */}
      {skills.length > 0 && (
        <div className="card">
          <h2 className="font-semibold text-gray-800 mb-4">Top Skills in Candidate Pool</h2>
          <div className="space-y-2">
            {skills.slice(0, 8).map((s, i) => {
              const max = skills[0]?.count || 1;
              return (
                <div key={i} className="flex items-center gap-3">
                  <div className="w-28 text-sm text-gray-600 truncate">{s.skill}</div>
                  <div className="flex-1 bg-gray-100 rounded-full h-2">
                    <div className="bg-primary-500 h-2 rounded-full transition-all"
                      style={{ width: `${(s.count / max) * 100}%` }} />
                  </div>
                  <div className="w-6 text-xs text-gray-400 text-right">{s.count}</div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Quick actions */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {[
          { to: '/upload', label: 'Upload Resumes', desc: 'Add new candidates', icon: Upload, color: 'text-primary-600 bg-primary-50' },
          { to: '/jobs',   label: 'Manage Jobs',    desc: 'Add job descriptions', icon: Briefcase, color: 'text-violet-600 bg-violet-50' },
          { to: '/resumes',label: 'View All Candidates', desc: 'Browse & filter', icon: FileText, color: 'text-emerald-600 bg-emerald-50' },
        ].map(({ to, label, desc, icon: Icon, color }) => (
          <Link key={to} to={to}
            className="card hover:shadow-md transition-shadow flex items-center gap-4 group">
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${color}`}>
              <Icon className="w-5 h-5" />
            </div>
            <div>
              <div className="font-medium text-gray-800 group-hover:text-primary-600 transition-colors">{label}</div>
              <div className="text-xs text-gray-400">{desc}</div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
