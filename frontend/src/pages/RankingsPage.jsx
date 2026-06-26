/**
 * pages/RankingsPage.jsx - Candidate Rankings for a Job
 */

import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { screeningAPI, reportsAPI, jobsAPI, downloadBlob } from '../utils/api';
import { Trophy, Download, FileSpreadsheet, ChevronRight, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import toast from 'react-hot-toast';

const REC_ICONS = {
  Selected: <CheckCircle className="w-4 h-4 text-green-500" />,
  Rejected:  <XCircle className="w-4 h-4 text-red-400" />,
  Maybe:     <AlertCircle className="w-4 h-4 text-yellow-500" />,
};

const MEDAL = ['🥇', '🥈', '🥉'];

export default function RankingsPage() {
  const { jobId } = useParams();
  const [rankings, setRankings] = useState([]);
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState('');

  useEffect(() => {
    Promise.all([
      screeningAPI.rankings(jobId),
      jobsAPI.get(jobId)
    ]).then(([r, j]) => {
      setRankings(r.data);
      setJob(j.data);
    }).catch(console.error)
    .finally(() => setLoading(false));
  }, [jobId]);

  const downloadPDF = async () => {
    setDownloading('pdf');
    try {
      const res = await reportsAPI.downloadPDF(jobId);
      downloadBlob(res.data, `report_${jobId}.pdf`);
      toast.success('PDF downloaded!');
    } catch { toast.error('PDF download failed'); }
    finally { setDownloading(''); }
  };

  const downloadExcel = async () => {
    setDownloading('excel');
    try {
      const res = await reportsAPI.downloadExcel(jobId);
      downloadBlob(res.data, `report_${jobId}.xlsx`);
      toast.success('Excel downloaded!');
    } catch { toast.error('Excel download failed'); }
    finally { setDownloading(''); }
  };

  if (loading) return <div className="flex justify-center py-12"><div className="w-8 h-8 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin" /></div>;

  return (
    <div className="space-y-5 max-w-5xl">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Trophy className="w-5 h-5 text-amber-500" />
            <h1 className="text-2xl font-bold text-gray-900">Candidate Rankings</h1>
          </div>
          {job && <p className="text-gray-500 text-sm">{job.title} · {rankings.length} candidates</p>}
        </div>
        <div className="flex gap-2 flex-shrink-0">
          <button onClick={downloadExcel} disabled={!!downloading}
            className="btn-secondary flex items-center gap-1.5 text-sm">
            <FileSpreadsheet className="w-4 h-4 text-green-600" />
            {downloading === 'excel' ? 'Downloading...' : 'Excel'}
          </button>
          <button onClick={downloadPDF} disabled={!!downloading}
            className="btn-secondary flex items-center gap-1.5 text-sm">
            <Download className="w-4 h-4 text-red-500" />
            {downloading === 'pdf' ? 'Downloading...' : 'PDF'}
          </button>
        </div>
      </div>

      {/* Stats row */}
      {rankings.length > 0 && (
        <div className="grid grid-cols-3 gap-4">
          {[
            { label: 'Selected', count: rankings.filter(r => r.recommendation === 'Selected').length, color: 'text-green-600 bg-green-50' },
            { label: 'Maybe',    count: rankings.filter(r => r.recommendation === 'Maybe').length,    color: 'text-yellow-600 bg-yellow-50' },
            { label: 'Rejected', count: rankings.filter(r => r.recommendation === 'Rejected').length, color: 'text-red-600 bg-red-50' },
          ].map(({ label, count, color }) => (
            <div key={label} className={`card text-center py-4 ${color}`}>
              <div className="text-2xl font-bold">{count}</div>
              <div className="text-sm font-medium">{label}</div>
            </div>
          ))}
        </div>
      )}

      {/* Rankings list */}
      {rankings.length === 0 ? (
        <div className="card text-center py-16">
          <Trophy className="w-12 h-12 text-gray-200 mx-auto mb-3" />
          <p className="text-gray-500">No scored candidates yet</p>
          <Link to="/upload" className="btn-primary mt-3 inline-block text-sm">Upload & Score Resumes</Link>
        </div>
      ) : (
        <div className="space-y-3">
          {rankings.map((c, i) => {
            const score = c.ats_score || 0;
            const barColor = score >= 75 ? 'bg-green-500' : score >= 50 ? 'bg-yellow-500' : 'bg-red-400';
            return (
              <div key={c.resume_id} className="card hover:shadow-md transition-shadow">
                <div className="flex items-center gap-4">
                  {/* Rank */}
                  <div className="w-10 text-center flex-shrink-0">
                    {i < 3
                      ? <span className="text-xl">{MEDAL[i]}</span>
                      : <span className="text-lg font-bold text-gray-400">#{c.rank}</span>}
                  </div>

                  {/* Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-0.5">
                      <span className="font-semibold text-gray-900">{c.candidate_name || 'Unknown'}</span>
                      {REC_ICONS[c.recommendation]}
                      <span className={c.recommendation === 'Selected' ? 'badge-selected' : c.recommendation === 'Rejected' ? 'badge-rejected' : 'badge-maybe'}>
                        {c.recommendation}
                      </span>
                    </div>
                    <p className="text-xs text-gray-500 line-clamp-1">{c.filename}</p>

                    {/* Score bar */}
                    <div className="flex items-center gap-2 mt-2">
                      <div className="flex-1 bg-gray-100 rounded-full h-2 max-w-xs">
                        <div className={`${barColor} h-2 rounded-full transition-all`} style={{ width: `${score}%` }} />
                      </div>
                      <span className="text-sm font-bold text-gray-700">{score.toFixed(1)}%</span>
                    </div>

                    {/* Skills */}
                    <div className="flex gap-1.5 mt-2 flex-wrap">
                      {c.skill_match?.slice(0, 4).map(s => (
                        <span key={s} className="text-xs bg-green-100 text-green-700 px-1.5 py-0.5 rounded">{s}</span>
                      ))}
                      {c.missing_skills?.slice(0, 3).map(s => (
                        <span key={s} className="text-xs bg-red-100 text-red-600 px-1.5 py-0.5 rounded">{s} ✗</span>
                      ))}
                    </div>
                  </div>

                  <Link to={`/resumes/${c.resume_id}`}
                    className="p-2 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded-lg flex-shrink-0">
                    <ChevronRight className="w-5 h-5" />
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
