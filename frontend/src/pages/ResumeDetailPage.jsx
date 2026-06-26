/**
 * pages/ResumeDetailPage.jsx - Full Resume Analysis View
 */

import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { resumesAPI } from '../utils/api';
import { ArrowLeft, CheckCircle, XCircle, User, Mail, Phone, Briefcase, GraduationCap, Lightbulb } from 'lucide-react';

function ScoreRing({ score }) {
  const color = score >= 75 ? '#10b981' : score >= 50 ? '#f59e0b' : '#ef4444';
  const r = 36, c = 2 * Math.PI * r;
  const fill = ((score || 0) / 100) * c;
  return (
    <div className="flex flex-col items-center">
      <svg width="96" height="96" viewBox="0 0 96 96">
        <circle cx="48" cy="48" r={r} fill="none" stroke="#f1f5f9" strokeWidth="8" />
        <circle cx="48" cy="48" r={r} fill="none" stroke={color} strokeWidth="8"
          strokeDasharray={`${fill} ${c}`} strokeLinecap="round"
          transform="rotate(-90 48 48)" />
        <text x="48" y="53" textAnchor="middle" fontSize="18" fontWeight="700" fill={color}>{score?.toFixed(0) ?? '—'}%</text>
      </svg>
      <span className="text-xs text-gray-500 mt-1">ATS Score</span>
    </div>
  );
}

export default function ResumeDetailPage() {
  const { id } = useParams();
  const [resume, setResume] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    resumesAPI.get(id)
      .then(r => setResume(r.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="flex justify-center py-12"><div className="w-8 h-8 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin" /></div>;
  if (!resume) return <div className="text-center py-12 text-gray-500">Resume not found</div>;

  const p = resume.parsed_data || {};
  const rec = resume.recommendation;
  const recColor = rec === 'Selected' ? 'text-green-600 bg-green-50' : rec === 'Rejected' ? 'text-red-600 bg-red-50' : 'text-yellow-600 bg-yellow-50';

  return (
    <div className="max-w-4xl space-y-5">
      {/* Back */}
      <Link to="/resumes" className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700">
        <ArrowLeft className="w-4 h-4" /> Back to Candidates
      </Link>

      {/* Header card */}
      <div className="card">
        <div className="flex items-start gap-6">
          <div className="w-14 h-14 bg-primary-100 rounded-2xl flex items-center justify-center flex-shrink-0">
            <User className="w-7 h-7 text-primary-600" />
          </div>
          <div className="flex-1 min-w-0">
            <h1 className="text-xl font-bold text-gray-900">{p.name || 'Unknown Candidate'}</h1>
            <div className="flex flex-wrap gap-3 mt-1 text-sm text-gray-500">
              {p.email && <span className="flex items-center gap-1"><Mail className="w-3.5 h-3.5" />{p.email}</span>}
              {p.phone && <span className="flex items-center gap-1"><Phone className="w-3.5 h-3.5" />{p.phone}</span>}
              {p.total_experience_years > 0 && <span className="flex items-center gap-1"><Briefcase className="w-3.5 h-3.5" />{p.total_experience_years} yrs exp</span>}
            </div>
            {resume.summary && <p className="text-sm text-gray-600 mt-3 leading-relaxed">{resume.summary}</p>}
          </div>
          <div className="flex-shrink-0 flex flex-col items-end gap-3">
            <ScoreRing score={resume.ats_score} />
            {rec && <span className={`text-sm font-semibold px-3 py-1 rounded-full ${recColor}`}>{rec}</span>}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Skills match */}
        {(resume.skill_match?.length > 0 || resume.missing_skills?.length > 0) && (
          <div className="card">
            <h2 className="font-semibold text-gray-800 mb-3">Skill Analysis</h2>
            {resume.skill_match?.length > 0 && (
              <div className="mb-3">
                <div className="text-xs font-medium text-green-600 mb-1.5 flex items-center gap-1">
                  <CheckCircle className="w-3.5 h-3.5" /> Matched ({resume.skill_match.length})
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {resume.skill_match.map(s => <span key={s} className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">{s}</span>)}
                </div>
              </div>
            )}
            {resume.missing_skills?.length > 0 && (
              <div>
                <div className="text-xs font-medium text-red-500 mb-1.5 flex items-center gap-1">
                  <XCircle className="w-3.5 h-3.5" /> Missing ({resume.missing_skills.length})
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {resume.missing_skills.map(s => <span key={s} className="text-xs bg-red-100 text-red-600 px-2 py-0.5 rounded-full">{s}</span>)}
                </div>
              </div>
            )}
          </div>
        )}

        {/* All skills */}
        {p.skills?.length > 0 && (
          <div className="card">
            <h2 className="font-semibold text-gray-800 mb-3">All Detected Skills ({p.skills.length})</h2>
            <div className="flex flex-wrap gap-1.5">
              {p.skills.map(s => <span key={s} className="text-xs bg-primary-50 text-primary-600 px-2 py-0.5 rounded-full">{s}</span>)}
            </div>
          </div>
        )}

        {/* Education */}
        {p.education?.length > 0 && (
          <div className="card">
            <h2 className="font-semibold text-gray-800 mb-3 flex items-center gap-2"><GraduationCap className="w-4 h-4" /> Education</h2>
            <div className="space-y-2">
              {p.education.map((e, i) => (
                <div key={i} className="text-sm">
                  <div className="font-medium text-gray-800">{e.degree}</div>
                  {e.institution && <div className="text-gray-500">{e.institution}</div>}
                  {e.year && <div className="text-xs text-gray-400">{e.year}</div>}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Experience */}
        {p.experience?.length > 0 && (
          <div className="card">
            <h2 className="font-semibold text-gray-800 mb-3 flex items-center gap-2"><Briefcase className="w-4 h-4" /> Experience</h2>
            <div className="space-y-3">
              {p.experience.slice(0, 4).map((e, i) => (
                <div key={i} className="text-sm border-l-2 border-primary-200 pl-3">
                  <div className="font-medium text-gray-800">{e.title}</div>
                  {e.company && <div className="text-gray-500">{e.company}</div>}
                  {e.duration && <div className="text-xs text-gray-400">{e.duration}</div>}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Suggestions */}
      {resume.suggestions?.length > 0 && (
        <div className="card border-l-4 border-amber-400">
          <h2 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
            <Lightbulb className="w-4 h-4 text-amber-500" /> Recommendations
          </h2>
          <ul className="space-y-2">
            {resume.suggestions.map((s, i) => (
              <li key={i} className="text-sm text-gray-600 flex gap-2">
                <span className="text-amber-500 font-bold mt-0.5">•</span> {s}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
