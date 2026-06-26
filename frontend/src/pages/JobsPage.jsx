/**
 * pages/JobsPage.jsx - Job Description Management
 */

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { jobsAPI } from '../utils/api';
import { Plus, Briefcase, Users, Trash2, ChevronRight, X } from 'lucide-react';
import toast from 'react-hot-toast';

function CreateJobModal({ onClose, onCreate }) {
  const [form, setForm] = useState({
    title: '', description: '', required_skills: '', experience_years: 0
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.title || !form.description) { toast.error('Title and description required'); return; }
    setLoading(true);
    try {
      const skills = form.required_skills.split(',').map(s => s.trim()).filter(Boolean);
      await jobsAPI.create({ ...form, required_skills: skills, experience_years: Number(form.experience_years) });
      toast.success('Job created!');
      onCreate();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to create job');
    } finally { setLoading(false); }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg">
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="font-semibold text-gray-900">Create Job Description</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600"><X className="w-5 h-5" /></button>
        </div>
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Job Title *</label>
            <input className="input" placeholder="e.g. Senior Python Developer"
              value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Job Description *</label>
            <textarea className="input resize-none" rows={5}
              placeholder="Paste the full job description here..."
              value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Required Skills <span className="text-gray-400 font-normal">(comma-separated)</span></label>
            <input className="input" placeholder="Python, FastAPI, Docker, MongoDB"
              value={form.required_skills} onChange={e => setForm(f => ({ ...f, required_skills: e.target.value }))} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Min. Experience (years)</label>
            <input type="number" min="0" max="20" className="input w-32"
              value={form.experience_years} onChange={e => setForm(f => ({ ...f, experience_years: e.target.value }))} />
          </div>
          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose} className="btn-secondary flex-1">Cancel</button>
            <button type="submit" disabled={loading} className="btn-primary flex-1">
              {loading ? 'Creating...' : 'Create Job'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default function JobsPage() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);

  const fetchJobs = async () => {
    try {
      const res = await jobsAPI.list();
      setJobs(res.data);
    } catch { toast.error('Failed to load jobs'); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchJobs(); }, []);

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this job?')) return;
    try {
      await jobsAPI.delete(id);
      toast.success('Job deleted');
      fetchJobs();
    } catch { toast.error('Failed to delete'); }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Job Descriptions</h1>
          <p className="text-gray-500 text-sm mt-0.5">{jobs.length} job{jobs.length !== 1 ? 's' : ''} total</p>
        </div>
        <button onClick={() => setShowModal(true)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> New Job
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <div className="w-8 h-8 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin" />
        </div>
      ) : jobs.length === 0 ? (
        <div className="card text-center py-16">
          <Briefcase className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500 font-medium">No jobs yet</p>
          <p className="text-gray-400 text-sm mb-4">Create your first job description to start screening</p>
          <button onClick={() => setShowModal(true)} className="btn-primary">Create Job</button>
        </div>
      ) : (
        <div className="space-y-3">
          {jobs.map(job => (
            <div key={job.id} className="card hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-semibold text-gray-900">{job.title}</h3>
                    <span className="text-xs bg-primary-100 text-primary-700 px-2 py-0.5 rounded-full">
                      {job.experience_years}+ yrs
                    </span>
                  </div>
                  <p className="text-gray-500 text-sm line-clamp-2 mb-3">{job.description}</p>
                  <div className="flex flex-wrap gap-1.5 mb-3">
                    {job.required_skills.slice(0, 6).map(s => (
                      <span key={s} className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">{s}</span>
                    ))}
                    {job.required_skills.length > 6 && (
                      <span className="text-xs text-gray-400">+{job.required_skills.length - 6} more</span>
                    )}
                  </div>
                  <div className="flex items-center gap-4 text-xs text-gray-400">
                    <span className="flex items-center gap-1"><Users className="w-3 h-3" />{job.resume_count} candidates</span>
                    <span>{new Date(job.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  {job.resume_count > 0 && (
                    <Link to={`/rankings/${job.id}`}
                      className="btn-secondary text-sm flex items-center gap-1">
                      Rankings <ChevronRight className="w-3 h-3" />
                    </Link>
                  )}
                  <button onClick={() => handleDelete(job.id)}
                    className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {showModal && (
        <CreateJobModal onClose={() => setShowModal(false)} onCreate={() => { setShowModal(false); fetchJobs(); }} />
      )}
    </div>
  );
}
