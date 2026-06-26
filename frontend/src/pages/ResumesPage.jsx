/**
 * pages/ResumesPage.jsx - All Candidates with Search & Filter
 */

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { resumesAPI } from '../utils/api';
import { Search, Filter, User, Mail, ChevronRight, Trash2 } from 'lucide-react';
import toast from 'react-hot-toast';

function RecommendationBadge({ rec }) {
  const cls = rec === 'Selected' ? 'badge-selected' : rec === 'Rejected' ? 'badge-rejected' : rec === 'Maybe' ? 'badge-maybe' : 'badge-pending';
  return <span className={cls}>{rec || 'Pending'}</span>;
}

function ScoreBar({ score }) {
  if (score == null) return <span className="text-xs text-gray-400">Not scored</span>;
  const color = score >= 75 ? 'bg-green-500' : score >= 50 ? 'bg-yellow-500' : 'bg-red-400';
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 bg-gray-100 rounded-full h-1.5 w-20">
        <div className={`${color} h-1.5 rounded-full`} style={{ width: `${score}%` }} />
      </div>
      <span className="text-xs font-medium text-gray-600">{score.toFixed(0)}%</span>
    </div>
  );
}

export default function ResumesPage() {
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('');

  const fetchResumes = async () => {
    setLoading(true);
    try {
      const params = {};
      if (search) params.search = search;
      if (filter) params.recommendation = filter;
      const res = await resumesAPI.list(params);
      setResumes(res.data);
    } catch { toast.error('Failed to load resumes'); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchResumes(); }, [search, filter]);

  const handleDelete = async (id, e) => {
    e.preventDefault();
    if (!window.confirm('Delete this resume?')) return;
    try {
      await resumesAPI.delete(id);
      toast.success('Deleted');
      fetchResumes();
    } catch { toast.error('Failed to delete'); }
  };

  return (
    <div className="space-y-5 max-w-5xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">All Candidates</h1>
          <p className="text-gray-500 text-sm mt-0.5">{resumes.length} candidate{resumes.length !== 1 ? 's' : ''}</p>
        </div>
        <Link to="/upload" className="btn-primary text-sm">+ Upload</Link>
      </div>

      {/* Search & Filter */}
      <div className="flex gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input className="input pl-9" placeholder="Search by name or email..."
            value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <select className="input w-40" value={filter} onChange={e => setFilter(e.target.value)}>
          <option value="">All Status</option>
          <option value="Selected">Selected</option>
          <option value="Maybe">Maybe</option>
          <option value="Rejected">Rejected</option>
        </select>
      </div>

      {/* Table */}
      {loading ? (
        <div className="flex justify-center py-12">
          <div className="w-8 h-8 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin" />
        </div>
      ) : resumes.length === 0 ? (
        <div className="card text-center py-16">
          <User className="w-12 h-12 text-gray-200 mx-auto mb-3" />
          <p className="text-gray-500">No candidates found</p>
          <Link to="/upload" className="btn-primary mt-3 inline-block text-sm">Upload Resumes</Link>
        </div>
      ) : (
        <div className="card p-0 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                {['Candidate', 'Skills', 'Experience', 'ATS Score', 'Status', ''].map(h => (
                  <th key={h} className="text-left text-xs font-medium text-gray-500 uppercase tracking-wide px-4 py-3">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {resumes.map(r => (
                <tr key={r.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3">
                    <div className="font-medium text-gray-900">{r.candidate_name || <span className="text-gray-400 italic">Unknown</span>}</div>
                    <div className="text-xs text-gray-400 flex items-center gap-1 mt-0.5">
                      <Mail className="w-3 h-3" />{r.candidate_email || r.filename}
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-1">
                      {r.skills?.slice(0, 3).map(s => (
                        <span key={s} className="text-xs bg-primary-50 text-primary-600 px-1.5 py-0.5 rounded">{s}</span>
                      ))}
                      {r.skills?.length > 3 && <span className="text-xs text-gray-400">+{r.skills.length - 3}</span>}
                    </div>
                  </td>
                  <td className="px-4 py-3 text-gray-600 text-xs">
                    {r.parsed_data?.total_experience_years != null
                      ? `${r.parsed_data.total_experience_years} yr${r.parsed_data.total_experience_years !== 1 ? 's' : ''}`
                      : '—'}
                  </td>
                  <td className="px-4 py-3"><ScoreBar score={r.ats_score} /></td>
                  <td className="px-4 py-3"><RecommendationBadge rec={r.recommendation} /></td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1">
                      <Link to={`/resumes/${r.id}`} className="p-1.5 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded-lg">
                        <ChevronRight className="w-4 h-4" />
                      </Link>
                      <button onClick={(e) => handleDelete(r.id, e)} className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
