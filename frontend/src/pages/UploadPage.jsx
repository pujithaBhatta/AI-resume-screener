/**
 * pages/UploadPage.jsx - Resume Upload with Drag & Drop
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { resumesAPI, jobsAPI, screeningAPI } from '../utils/api';
import { jobsAPI as jAPI } from '../utils/api';
import { Upload, File, CheckCircle, XCircle, Loader, X, Play } from 'lucide-react';
import toast from 'react-hot-toast';

export default function UploadPage() {
  const [files, setFiles]         = useState([]);
  const [jobs, setJobs]           = useState([]);
  const [selectedJob, setSelectedJob] = useState('');
  const [uploading, setUploading] = useState(false);
  const [scoring, setScoring]     = useState(false);
  const [results, setResults]     = useState([]);

  useEffect(() => {
    jobsAPI.list().then(r => setJobs(r.data)).catch(() => {});
  }, []);

  const onDrop = useCallback((accepted, rejected) => {
    if (rejected.length) toast.error(`${rejected.length} file(s) rejected. Use PDF or DOCX only.`);
    setFiles(prev => {
      const newFiles = accepted.filter(f => !prev.find(p => p.name === f.name));
      return [...prev, ...newFiles];
    });
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'], 'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'] },
    maxSize: 10 * 1024 * 1024,
  });

  const removeFile = (name) => setFiles(f => f.filter(x => x.name !== name));

  const handleUpload = async () => {
    if (!files.length) { toast.error('Add at least one resume file'); return; }
    setUploading(true);
    setResults([]);
    try {
      const res = await resumesAPI.upload(files, selectedJob || null);
      setResults(res.data.results);
      toast.success(`${res.data.results.filter(r => r.status === 'success').length} resume(s) uploaded!`);
      
      // Auto-score if a job is selected
      if (selectedJob) {
        const successIds = res.data.results
          .filter(r => r.status === 'success')
          .map(r => r.id);
        if (successIds.length) {
          setScoring(true);
          try {
            await screeningAPI.score(selectedJob, successIds);
            toast.success('ATS scoring complete!');
          } catch { toast.error('Scoring failed — try from Rankings page'); }
          finally { setScoring(false); }
        }
      }
      setFiles([]);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Upload failed');
    } finally { setUploading(false); }
  };

  const busy = uploading || scoring;

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Upload Resumes</h1>
        <p className="text-gray-500 text-sm mt-0.5">Upload PDF or DOCX resumes for automatic parsing and ATS scoring</p>
      </div>

      {/* Job selector */}
      <div className="card">
        <label className="block text-sm font-medium text-gray-700 mb-1.5">
          Match Against Job Description <span className="text-gray-400 font-normal">(optional but recommended)</span>
        </label>
        <select className="input" value={selectedJob} onChange={e => setSelectedJob(e.target.value)}>
          <option value="">— Select a job to auto-score —</option>
          {jobs.map(j => <option key={j.id} value={j.id}>{j.title}</option>)}
        </select>
        {!jobs.length && (
          <p className="text-xs text-amber-600 mt-1.5">
            No jobs yet. <a href="/jobs" className="underline">Create a job first</a> to enable ATS scoring.
          </p>
        )}
      </div>

      {/* Drop zone */}
      <div className="card">
        <div {...getRootProps()}
          className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors ${
            isDragActive ? 'border-primary-400 bg-primary-50' : 'border-gray-200 hover:border-primary-300 hover:bg-gray-50'
          }`}>
          <input {...getInputProps()} />
          <Upload className={`w-10 h-10 mx-auto mb-3 ${isDragActive ? 'text-primary-500' : 'text-gray-300'}`} />
          {isDragActive ? (
            <p className="text-primary-600 font-medium">Drop files here!</p>
          ) : (
            <>
              <p className="text-gray-600 font-medium">Drag & drop resumes here</p>
              <p className="text-gray-400 text-sm mt-1">or click to browse</p>
              <p className="text-gray-300 text-xs mt-3">PDF, DOCX · Max 10MB each · Multiple files supported</p>
            </>
          )}
        </div>

        {/* File list */}
        {files.length > 0 && (
          <div className="mt-4 space-y-2">
            <p className="text-sm font-medium text-gray-700">{files.length} file{files.length > 1 ? 's' : ''} ready</p>
            {files.map(f => (
              <div key={f.name} className="flex items-center gap-3 bg-gray-50 rounded-lg px-3 py-2">
                <File className="w-4 h-4 text-primary-500 flex-shrink-0" />
                <span className="text-sm text-gray-700 flex-1 truncate">{f.name}</span>
                <span className="text-xs text-gray-400">{(f.size / 1024).toFixed(0)} KB</span>
                <button onClick={() => removeFile(f.name)} className="text-gray-400 hover:text-red-500">
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        )}

        <button onClick={handleUpload} disabled={busy || !files.length}
          className="btn-primary w-full mt-4 flex items-center justify-center gap-2 py-2.5">
          {busy ? (
            <>
              <Loader className="w-4 h-4 animate-spin" />
              {uploading ? 'Uploading & Parsing...' : 'Running ATS Scoring...'}
            </>
          ) : (
            <><Upload className="w-4 h-4" /> Upload {files.length > 0 ? `${files.length} File${files.length > 1 ? 's' : ''}` : 'Resumes'}</>
          )}
        </button>
      </div>

      {/* Results */}
      {results.length > 0 && (
        <div className="card">
          <h2 className="font-semibold text-gray-800 mb-3">Upload Results</h2>
          <div className="space-y-2">
            {results.map((r, i) => (
              <div key={i} className={`flex items-center gap-3 p-3 rounded-lg ${
                r.status === 'success' ? 'bg-green-50' : 'bg-red-50'
              }`}>
                {r.status === 'success'
                  ? <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
                  : <XCircle className="w-5 h-5 text-red-500 flex-shrink-0" />}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-800 truncate">{r.filename}</p>
                  <p className="text-xs text-gray-500">
                    {r.status === 'success'
                      ? `Parsed: ${r.candidate_name || 'Name not found'} · ${r.skills_found} skills detected`
                      : r.message}
                  </p>
                </div>
              </div>
            ))}
          </div>
          {selectedJob && (
            <a href={`/rankings/${selectedJob}`}
              className="btn-primary w-full mt-3 flex items-center justify-center gap-2 text-sm">
              <Play className="w-4 h-4" /> View Rankings
            </a>
          )}
        </div>
      )}
    </div>
  );
}
