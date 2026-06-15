'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface MediaAsset {
  id: number;
  type: 'image' | 'video';
  url: string;
  storage_url: string;
  filename: string;
  prompt: string;
  model: string;
  signed_url: string;
  posted_insta: boolean;
  posted_yt: boolean;
  yt_url?: string;
  alt_text: string;
  description: string;
  created_at: string;
}

interface QueueItem {
  id: number;
  prompt: string;
  yt_post: boolean;
  generated: boolean;
  insta_post: boolean;
  created_at: string;
}

interface GCSFile {
  name: string;
  id: string;
  size: number;
  contentType: string;
  updated: string;
}

interface AnalyticsData {
  counts: {
    images: number;
    videos: number;
    imagesQueue: number;
    videosQueue: number;
    postedInstaImages: number;
    postedInstaVideos: number;
    postedYtVideos: number;
  };
  sums: {
    impressions: number;
    reach: number;
    likes: number;
    comments: number;
    shares: number;
    saves: number;
  };
  recent: any[];
}

export default function DashboardPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'overview' | 'media' | 'queue' | 'storage' | 'analytics'>('overview');

  // Data States
  const [mediaAssets, setMediaAssets] = useState<MediaAsset[]>([]);
  const [mediaFilter, setMediaFilter] = useState<'all' | 'image' | 'video'>('all');
  const [imagesQueue, setImagesQueue] = useState<QueueItem[]>([]);
  const [videosQueue, setVideosQueue] = useState<QueueItem[]>([]);
  const [gcsFiles, setGcsFiles] = useState<GCSFile[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsData>({
    counts: { images: 0, videos: 0, imagesQueue: 0, videosQueue: 0, postedInstaImages: 0, postedInstaVideos: 0, postedYtVideos: 0 },
    sums: { impressions: 0, reach: 0, likes: 0, comments: 0, shares: 0, saves: 0 },
    recent: [],
  });

  // UI States
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');
  const [signingUrlId, setSigningUrlId] = useState<string | null>(null);
  const [activePreviews, setActivePreviews] = useState<Record<string, string>>({}); // maps asset unique key -> signed URL
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Theme State
  const [isLightMode, setIsLightMode] = useState(false);

  // Load theme preference on mount
  useEffect(() => {
    const saved = localStorage.getItem('isLightMode') === 'true';
    setIsLightMode(saved);
  }, []);

  // Toggle theme utility
  const toggleLightMode = () => {
    setIsLightMode((prev) => {
      const newVal = !prev;
      localStorage.setItem('isLightMode', String(newVal));
      return newVal;
    });
  };

  // Nav Link class utility
  const getNavBtnClass = (tab: 'overview' | 'media' | 'queue' | 'storage' | 'analytics') => {
    const isActive = activeTab === tab;
    if (isActive) {
      return isLightMode
        ? 'bg-blue-50 text-blue-600 border border-blue-200 shadow-sm shadow-blue-100/30 font-semibold'
        : 'bg-blue-600/15 text-blue-400 border border-blue-500/20 shadow-[0_0_15px_-3px_rgba(37,99,235,0.25)]';
    } else {
      return isLightMode
        ? 'text-slate-500 hover:text-slate-900 hover:bg-slate-100/50 border border-transparent'
        : 'text-zinc-400 hover:text-zinc-100 hover:bg-zinc-900/40 border border-transparent';
    }
  };

  // Date Formatting Utilities (IST Time Zone)
  const formatToIST = (dateString: string | Date) => {
    try {
      const date = new Date(dateString);
      if (isNaN(date.getTime())) return 'N/A';
      return date.toLocaleString('en-IN', {
        timeZone: 'Asia/Kolkata',
        hour12: true,
        day: 'numeric',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      }) + ' IST';
    } catch (e) {
      return 'N/A';
    }
  };

  const formatDateToIST = (dateString: string | Date) => {
    try {
      const date = new Date(dateString);
      if (isNaN(date.getTime())) return 'N/A';
      return date.toLocaleDateString('en-IN', {
        timeZone: 'Asia/Kolkata',
        day: 'numeric',
        month: 'short',
        year: 'numeric'
      }) + ' IST';
    } catch (e) {
      return 'N/A';
    }
  };

  // Form State
  const [newPrompt, setNewPrompt] = useState('');
  const [newType, setNewType] = useState<'image' | 'video'>('image');
  const [autoInsta, setAutoInsta] = useState(true);
  const [autoYt, setAutoYt] = useState(false);
  const [submittingPrompt, setSubmittingPrompt] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  // Fetch all dashboard data
  const fetchData = async () => {
    setLoading(true);
    setErrorMsg('');
    try {
      // Fetch media
      const mediaRes = await fetch('/api/media');
      const mediaData = await mediaRes.json();
      if (mediaRes.ok && mediaData.success) {
        setMediaAssets(mediaData.allMedia);
      } else {
        console.warn('Media fetch returned warning:', mediaData.error);
      }

      // Fetch queues
      const queueRes = await fetch('/api/queue');
      const queueData = await queueRes.json();
      if (queueRes.ok && queueData.success) {
        setImagesQueue(queueData.imagesQueue);
        setVideosQueue(queueData.videosQueue);
      }

      // Fetch analytics
      const analyticsRes = await fetch('/api/analytics');
      const analyticsData = await analyticsRes.json();
      if (analyticsRes.ok) {
        setAnalytics(analyticsData);
      }

      // Fetch GCS files
      const storageRes = await fetch('/api/storage');
      const storageData = await storageRes.json();
      if (storageRes.ok && storageData.success) {
        setGcsFiles(storageData.files);
      }
    } catch (err: any) {
      console.error('Error fetching dashboard data:', err);
      setErrorMsg('Failed to load dashboard data. Ensure connection is stable.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Handle previewing private media
  const handlePreviewMedia = async (asset: MediaAsset | string, uniqueKey: string) => {
    if (activePreviews[uniqueKey]) {
      // Toggle off if already previewing
      const updated = { ...activePreviews };
      delete updated[uniqueKey];
      setActivePreviews(updated);
      return;
    }

    setSigningUrlId(uniqueKey);
    try {
      const filename = typeof asset === 'string' ? asset : asset.filename;
      const res = await fetch(`/api/media/signed-url?filename=${encodeURIComponent(filename)}`);
      const data = await res.json();

      if (res.ok && data.success) {
        setActivePreviews((prev) => ({
          ...prev,
          [uniqueKey]: data.signedUrl,
        }));
      } else {
        alert('Could not generate secure link: ' + (data.error || 'Unknown error'));
      }
    } catch (err) {
      console.error('Failed to request signed GCS URL:', err);
      alert('Error fetching signed URL.');
    } finally {
      setSigningUrlId(null);
    }
  };

  // Enqueue new prompt
  const handleAddPrompt = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newPrompt.trim()) return;

    setSubmittingPrompt(true);
    setSubmitSuccess(false);
    try {
      const res = await fetch('/api/queue', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: newType,
          prompt: newPrompt,
          instaPost: autoInsta,
          ytPost: autoYt,
        }),
      });
      const data = await res.json();

      if (res.ok && data.success) {
        setNewPrompt('');
        setSubmitSuccess(true);
        // Refresh queue lists and analytics counts
        fetchData();
        setTimeout(() => setSubmitSuccess(false), 4000);
      } else {
        alert(data.error || 'Failed to add item to queue.');
      }
    } catch (err) {
      console.error('Error adding to queue:', err);
      alert('Network error enqueuing prompt.');
    } finally {
      setSubmittingPrompt(false);
    }
  };

  // Delete item from queue
  const handleDeleteQueueItem = async (type: 'image' | 'video', id: number) => {
    if (!confirm('Are you sure you want to remove this item from the generation queue?')) return;

    try {
      const res = await fetch(`/api/queue?type=${type}&id=${id}`, {
        method: 'DELETE',
      });
      const data = await res.json();

      if (res.ok && data.success) {
        fetchData();
      } else {
        alert(data.error || 'Failed to delete queue item.');
      }
    } catch (err) {
      console.error('Error deleting queue item:', err);
      alert('Network error deleting queue item.');
    }
  };

  // Logout
  const handleLogout = async () => {
    try {
      await fetch('/api/auth/logout', { method: 'POST' });
      router.push('/login');
      router.refresh();
    } catch (err) {
      console.error('Logout error:', err);
    }
  };

  // Bytes size formatter
  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const filteredMedia = mediaAssets.filter((asset) => {
    if (mediaFilter === 'all') return true;
    return asset.type === mediaFilter;
  });

  return (
    <div className={`flex h-screen overflow-hidden font-sans transition-colors duration-300 ${
      isLightMode ? 'bg-[#f0f4f8] text-slate-800' : 'bg-[#090b16] text-zinc-100'
    }`}>
      {/* Dynamic Glow Orbs */}
      <div className={`absolute top-0 right-0 w-[400px] h-[400px] rounded-full blur-[120px] pointer-events-none transition-colors duration-500 ${
        isLightMode ? 'bg-blue-500/5' : 'bg-blue-900/10'
      }`} />
      <div className={`absolute bottom-0 left-0 w-[500px] h-[500px] rounded-full blur-[150px] pointer-events-none transition-colors duration-500 ${
        isLightMode ? 'bg-cyan-500/5' : 'bg-cyan-900/10'
      }`} />

      {/* Sidebar - Mobile Toggle */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-64 backdrop-blur-md transform transition-transform duration-300 md:relative md:translate-x-0
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
        ${isLightMode ? 'bg-white/95 border-r border-slate-200 shadow-lg shadow-slate-100/50' : 'bg-zinc-955/80 border-r border-zinc-900'}
      `}>
        <div className="flex flex-col h-full">
          {/* Logo Section */}
          <div className={`flex items-center gap-3 px-6 py-6 border-b transition-colors duration-300 ${
            isLightMode ? 'border-slate-200' : 'border-zinc-900'
          }`}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-cyan-500 flex items-center justify-center shadow-[0_0_15px_rgba(37,99,235,0.4)]">
              <span className="text-white font-black text-lg">SF</span>
            </div>
            <div>
              <h2 className={`font-bold tracking-tight leading-none text-base transition-colors duration-300 ${
                isLightMode ? 'text-slate-900' : 'text-white'
              }`}>Synaptic Flow</h2>
              <span className={`text-[10px] font-mono uppercase tracking-widest mt-1.5 inline-block transition-colors duration-300 ${
                isLightMode ? 'text-slate-400' : 'text-zinc-500'
              }`}>Post Control</span>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto">
            <button
              onClick={() => { setActiveTab('overview'); setSidebarOpen(false); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${getNavBtnClass('overview')}`}
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5">
                <path strokeLinecap="round" strokeLinejoin="round" d="m2.25 12 8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" />
              </svg>
              Overview
            </button>

            <button
              onClick={() => { setActiveTab('media'); setSidebarOpen(false); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${getNavBtnClass('media')}`}
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5">
                <path strokeLinecap="round" strokeLinejoin="round" d="m2.25 15.75 5.159-5.159a2.25 2.25 0 0 1 3.182 0l5.159 5.159m-1.5-1.5 1.409-1.409a2.25 2.25 0 0 1 3.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 0 0 1.5-1.5V6a1.5 1.5 0 0 0-1.5-1.5H3.75A1.5 1.5 0 0 0 2.25 6v12a1.5 1.5 0 0 0 1.5 1.5Zm10.5-11.25h.008v.008h-.008V8.25Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Z" />
              </svg>
              Media Gallery
            </button>

            <button
              onClick={() => { setActiveTab('queue'); setSidebarOpen(false); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${getNavBtnClass('queue')}`}
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 12h16.5m-16.5 3.75h16.5M3.75 19.5h16.5M5.625 4.5h12.75c.621 0 1.125.504 1.125 1.125v1.875c0 .621-.504 1.125-1.125 1.125H5.625A1.125 1.125 0 0 1 4.5 7.5V5.625c0-.621.504-1.125 1.125-1.125Z" />
              </svg>
              Pipeline Queue
              {(imagesQueue.length + videosQueue.length) > 0 && (
                <span className="ml-auto px-2 py-0.5 text-xs font-bold rounded-full bg-blue-600 text-white animate-pulse">
                  {imagesQueue.length + videosQueue.length}
                </span>
              )}
            </button>

            <button
              onClick={() => { setActiveTab('storage'); setSidebarOpen(false); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${getNavBtnClass('storage')}`}
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 7.5l-.625 10.632a2.25 2.25 0 0 1-2.247 2.118H6.622a2.25 2.25 0 0 1-2.247-2.118L3.75 7.5M10 11.25h4M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z" />
              </svg>
              GCS Bucket Files
            </button>

            <button
              onClick={() => { setActiveTab('analytics'); setSidebarOpen(false); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${getNavBtnClass('analytics')}`}
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 6a7.5 7.5 0 1 0 7.5 7.5h-7.5V6Z" />
                <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 10.5H21A7.5 7.5 0 0 0 13.5 3v7.5Z" />
              </svg>
              Analytics
            </button>
          </nav>

          {/* User Settings & Logout */}
          <div className={`p-4 border-t transition-colors duration-300 ${
            isLightMode ? 'border-slate-205/80' : 'border-zinc-900'
          }`}>
            <button
              onClick={handleLogout}
              className={`w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-xs font-semibold border transition-all ${
                isLightMode 
                  ? 'text-slate-500 hover:text-red-650 hover:bg-red-50 border-transparent hover:border-red-200' 
                  : 'text-zinc-400 hover:text-white hover:bg-red-955/25 border-transparent hover:border-red-900/30'
              }`}
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4.5 h-4.5 text-zinc-500 shrink-0">
                <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0 0 13.5 3h-6a2.25 2.25 0 0 0-2.25 2.25v13.5A2.25 2.25 0 0 0 7.5 21h6a2.25 2.25 0 0 0 2.25-2.25V15M12 9l-3 3m0 0 3 3m-3-3h12.75" />
              </svg>
              Sign Out Session
            </button>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden relative z-10">
        {/* Header bar */}
        <header className={`flex items-center justify-between px-6 py-4 border-b backdrop-blur-md transition-colors duration-300 ${
          isLightMode ? 'bg-white/70 border-slate-200' : 'bg-zinc-955/50 border-zinc-900'
        }`}>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(true)}
              className={`p-2 -ml-2 md:hidden transition-colors ${isLightMode ? 'text-slate-500 hover:text-slate-800' : 'text-zinc-400 hover:text-white'}`}
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-6 h-6">
                <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
              </svg>
            </button>
            <h1 className={`text-lg font-bold capitalize tracking-wide transition-colors duration-300 ${
              isLightMode ? 'text-slate-900' : 'text-white'
            }`}>
              {activeTab} Management
            </h1>
          </div>

          <div className="flex items-center gap-3.5">
            {/* Theme Toggle Button */}
            <button
              onClick={toggleLightMode}
              className={`p-2 rounded-xl border transition-all ${
                isLightMode 
                  ? 'text-amber-500 hover:bg-slate-100 border-slate-200 bg-white' 
                  : 'text-zinc-400 hover:text-white hover:bg-zinc-900/50 border-zinc-800 bg-zinc-950/20'
              }`}
              title={isLightMode ? "Switch to Dark Mode" : "Switch to Light Mode"}
            >
              {isLightMode ? (
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v2.25m0 13.5V21M5.136 5.136l1.591 1.591m9.093 9.093l1.591 1.591M3 12h2.25m13.5 0H21M5.136 18.864l1.591-1.591m9.093-9.093l1.591-1.591M12 7.5a4.5 4.5 0 1 1 0 9 4.5 4.5 0 0 1 0-9Z" />
                </svg>
              ) : (
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M21.752 15.002A9.72 9.72 0 0 1 18 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 0 0 3 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 0 0 9.002-5.998Z" />
                </svg>
              )}
            </button>

            {/* Sync Refresh Button */}
            <button
              onClick={fetchData}
              disabled={loading}
              className={`p-2 rounded-xl border disabled:opacity-50 transition-all ${
                isLightMode 
                  ? 'text-slate-600 hover:text-slate-900 hover:bg-slate-100 border-slate-200 bg-white' 
                  : 'text-zinc-400 hover:text-white hover:bg-zinc-900/50 border-zinc-800 bg-zinc-950/20'
              }`}
              title="Sync Dashboard Data"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99" />
              </svg>
            </button>
            <div className={`hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              isLightMode 
                ? 'bg-emerald-50 border border-emerald-200 text-emerald-600' 
                : 'bg-emerald-950/20 border border-emerald-900/40 text-emerald-400'
            }`}>
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
              Connected to Neon DB
            </div>
          </div>
        </header>

        {/* Dashboard Panels Wrapper */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8 space-y-6">
          {errorMsg && (
            <div className={`p-4 rounded-xl text-sm flex items-center justify-between transition-colors duration-300 ${
              isLightMode ? 'bg-red-50 border border-red-200 text-red-750' : 'bg-red-955/25 border border-red-900/40 text-red-300'
            }`}>
              <span className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-red-500" />
                {errorMsg}
              </span>
              <button onClick={() => setErrorMsg('')} className={`transition-colors ${
                isLightMode ? 'text-slate-400 hover:text-slate-700' : 'text-zinc-500 hover:text-white'
              }`}>Dismiss</button>
            </div>
          )}

          {loading && mediaAssets.length === 0 ? (
            <div className="h-64 flex flex-col items-center justify-center gap-4">
              <svg className="animate-spin h-10 w-10 text-blue-500" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              <span className={`font-mono text-sm transition-colors duration-300 ${
                isLightMode ? 'text-slate-500' : 'text-zinc-400'
              }`}>Syncing Cloud Assets...</span>
            </div>
          ) : (
            <>
              {/* TAB 1: OVERVIEW */}
              {activeTab === 'overview' && (
                <div className="space-y-6">
                  {/* Project Banner Display */}
                  <div className={`relative w-full h-[180px] rounded-2xl overflow-hidden border transition-all duration-300 shadow-sm ${
                    isLightMode 
                      ? 'bg-gradient-to-r from-blue-600 to-cyan-500 border-transparent' 
                      : 'bg-zinc-900 border-zinc-800/80 shadow-xl'
                  }`}>
                    <div className={`absolute inset-0 bg-gradient-to-t transition-colors duration-300 ${
                      isLightMode ? 'from-black/40 via-black/10 to-transparent' : 'from-[#090b16] via-[#090b16]/30 to-transparent'
                    }`} />
                    <div className="absolute bottom-6 left-6 space-y-1">
                      <span className="px-2.5 py-0.5 bg-blue-600/90 text-white rounded-full text-[9px] font-bold tracking-widest uppercase font-mono shadow-[0_0_10px_rgba(37,99,235,0.4)]">
                        Console Dashboard
                      </span>
                      <h2 className="text-2xl font-black tracking-tight text-white">Automated Social Media Pipeline</h2>
                    </div>
                  </div>

                  {/* Grid Widgets */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
                    {/* Widget 1 */}
                    <div className={`backdrop-blur-md border p-5 rounded-2xl flex items-center justify-between transition-all duration-300 ${
                      isLightMode 
                        ? 'bg-white border-slate-200 shadow-sm hover:border-blue-500/40 shadow-slate-100/50' 
                        : 'bg-zinc-900/40 border-zinc-800/80 hover:border-blue-500/25'
                    }`}>
                      <div>
                        <span className={`text-xs font-semibold uppercase tracking-wider block transition-colors duration-300 ${
                          isLightMode ? 'text-slate-400' : 'text-zinc-500'
                        }`}>Images Generated</span>
                        <span className={`text-3xl font-extrabold mt-1.5 block transition-colors duration-300 ${
                          isLightMode ? 'text-slate-900' : 'text-white'
                        }`}>{analytics.counts.images}</span>
                      </div>
                      <div className={`w-12 h-12 rounded-xl flex items-center justify-center transition-colors duration-300 ${
                        isLightMode 
                          ? 'bg-blue-50 border border-blue-100 text-blue-600' 
                          : 'bg-blue-600/10 border border-blue-500/20 text-blue-400'
                      }`}>
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-6 h-6">
                          <path strokeLinecap="round" strokeLinejoin="round" d="m2.25 15.75 5.159-5.159a2.25 2.25 0 0 1 3.182 0l5.159 5.159m-1.5-1.5 1.409-1.409a2.25 2.25 0 0 1 3.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 0 0 1.5-1.5V6a1.5 1.5 0 0 0-1.5-1.5H3.75A1.5 1.5 0 0 0 2.25 6v12a1.5 1.5 0 0 0 1.5 1.5Zm10.5-11.25h.008v.008h-.008V8.25Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Z" />
                        </svg>
                      </div>
                    </div>

                    {/* Widget 2 */}
                    <div className={`backdrop-blur-md border p-5 rounded-2xl flex items-center justify-between transition-all duration-300 ${
                      isLightMode 
                        ? 'bg-white border-slate-200 shadow-sm hover:border-cyan-500/40 shadow-slate-100/50' 
                        : 'bg-zinc-900/40 border-zinc-800/80 hover:border-cyan-500/25'
                    }`}>
                      <div>
                        <span className={`text-xs font-semibold uppercase tracking-wider block transition-colors duration-300 ${
                          isLightMode ? 'text-slate-400' : 'text-zinc-500'
                        }`}>Videos Generated</span>
                        <span className={`text-3xl font-extrabold mt-1.5 block transition-colors duration-300 ${
                          isLightMode ? 'text-slate-900' : 'text-white'
                        }`}>{analytics.counts.videos}</span>
                      </div>
                      <div className={`w-12 h-12 rounded-xl flex items-center justify-center transition-colors duration-300 ${
                        isLightMode 
                          ? 'bg-cyan-50 border border-cyan-100 text-cyan-600' 
                          : 'bg-cyan-600/10 border border-cyan-500/20 text-cyan-400'
                      }`}>
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-6 h-6">
                          <path strokeLinecap="round" strokeLinejoin="round" d="m15.75 10.5 4.72-4.72a.75.75 0 0 1 1.28.53v11.38a.75.75 0 0 1-1.28.53l-4.72-4.72M4.5 18.75h9a2.25 2.25 0 0 0 2.25-2.25v-9a2.25 2.25 0 0 0-2.25-2.25h-9A2.25 2.25 0 0 0 2.25 7.5v9a2.25 2.25 0 0 0 2.25 2.25Z" />
                        </svg>
                      </div>
                    </div>

                    {/* Widget 3 */}
                    <div className={`backdrop-blur-md border p-5 rounded-2xl flex items-center justify-between transition-all duration-300 ${
                      isLightMode 
                        ? 'bg-white border-slate-200 shadow-sm hover:border-yellow-500/40 shadow-slate-100/50' 
                        : 'bg-zinc-900/40 border-zinc-800/80 hover:border-yellow-500/25'
                    }`}>
                      <div>
                        <span className={`text-xs font-semibold uppercase tracking-wider block transition-colors duration-300 ${
                          isLightMode ? 'text-slate-400' : 'text-zinc-500'
                        }`}>Queued Prompts</span>
                        <span className={`text-3xl font-extrabold mt-1.5 block transition-colors duration-300 ${
                          isLightMode ? 'text-slate-900' : 'text-white'
                        }`}>
                          {analytics.counts.imagesQueue + analytics.counts.videosQueue}
                        </span>
                      </div>
                      <div className={`w-12 h-12 rounded-xl flex items-center justify-center transition-colors duration-300 ${
                        isLightMode 
                          ? 'bg-yellow-50 border border-yellow-100 text-yellow-600' 
                          : 'bg-yellow-600/10 border border-yellow-500/20 text-yellow-400'
                      }`}>
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-6 h-6">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
                        </svg>
                      </div>
                    </div>

                    {/* Widget 4 */}
                    <div className={`backdrop-blur-md border p-5 rounded-2xl flex items-center justify-between transition-all duration-300 ${
                      isLightMode 
                        ? 'bg-white border-slate-200 shadow-sm hover:border-emerald-500/40 shadow-slate-100/50' 
                        : 'bg-zinc-900/40 border-zinc-800/80 hover:border-emerald-500/25'
                    }`}>
                      <div>
                        <span className={`text-xs font-semibold uppercase tracking-wider block transition-colors duration-300 ${
                          isLightMode ? 'text-slate-400' : 'text-zinc-500'
                        }`}>Instagram Shares</span>
                        <span className={`text-3xl font-extrabold mt-1.5 block transition-colors duration-300 ${
                          isLightMode ? 'text-slate-900' : 'text-white'
                        }`}>
                          {analytics.counts.postedInstaImages + analytics.counts.postedInstaVideos}
                        </span>
                      </div>
                      <div className={`w-12 h-12 rounded-xl flex items-center justify-center transition-colors duration-300 ${
                        isLightMode 
                          ? 'bg-emerald-50 border border-emerald-100 text-emerald-600' 
                          : 'bg-emerald-600/10 border border-emerald-500/20 text-emerald-400'
                      }`}>
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-6 h-6">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M7.217 10.907a2.25 2.25 0 100 2.186m0-2.186l9.566-5.314m-9.566 7.5l9.566 5.314m0 0a2.25 2.25 0 103.935 2.186 2.25 2.25 0 0 0-3.935-2.186zm0-12.814a2.25 2.25 0 103.933-2.185 2.25 2.25 0 0 0-3.933 2.185z" />
                        </svg>
                      </div>
                    </div>
                  </div>

                  {/* Main Grid: Latest Release Feed + Queue Quick View */}
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Latest Release feed */}
                    <div className={`backdrop-blur-md border rounded-2xl p-6 transition-all duration-300 ${
                      isLightMode ? 'bg-white border-slate-200 shadow-sm shadow-slate-100/50' : 'bg-zinc-955/40 border-zinc-900'
                    }`}>
                      <div className="flex items-center justify-between mb-5">
                        <h3 className={`font-bold text-base transition-colors ${
                          isLightMode ? 'text-slate-900' : 'text-white'
                        }`}>Latest Media Outputs</h3>
                        <button onClick={() => setActiveTab('media')} className="text-xs text-blue-600 hover:text-blue-500 font-medium">View All</button>
                      </div>

                      {mediaAssets.length === 0 ? (
                        <div className="text-center py-12 text-zinc-500 text-sm font-mono">No outputs found in the database yet.</div>
                      ) : (
                        <div className={`divide-y transition-colors duration-300 ${
                          isLightMode ? 'divide-slate-100' : 'divide-zinc-900'
                        }`}>
                          {mediaAssets.slice(0, 5).map((asset) => {
                            const uniqueKey = `${asset.type}-${asset.id}`;
                            const previewUrl = activePreviews[uniqueKey] || asset.signed_url;

                            return (
                              <div key={uniqueKey} className="py-4 first:pt-0 last:pb-0 flex flex-col md:flex-row gap-4 items-start justify-between">
                                <div className="flex gap-4">
                                  {/* Thumbnail Preview Area */}
                                  <div className={`relative w-16 h-16 rounded-xl border flex-shrink-0 overflow-hidden flex items-center justify-center transition-colors ${
                                    isLightMode ? 'bg-slate-100 border-slate-200' : 'bg-zinc-900 border-zinc-800'
                                  }`}>
                                    {previewUrl ? (
                                      asset.type === 'image' ? (
                                        // eslint-disable-next-line @next/next/no-img-element
                                        <img src={previewUrl} alt={asset.alt_text} className="object-cover w-full h-full" />
                                      ) : (
                                        <video src={previewUrl} className="object-cover w-full h-full" muted />
                                      )
                                    ) : (
                                      <div className={`flex flex-col items-center justify-center text-[10px] font-mono transition-colors ${
                                        isLightMode ? 'text-slate-450' : 'text-zinc-600'
                                      }`}>
                                        <span>{asset.type.toUpperCase()}</span>
                                      </div>
                                    )}
                                  </div>

                                  <div>
                                    <h4 className={`font-semibold text-sm line-clamp-1 transition-colors ${
                                      isLightMode ? 'text-slate-800' : 'text-white'
                                    }`}>{asset.prompt}</h4>
                                    <p className={`text-xs font-mono mt-1 transition-colors ${
                                      isLightMode ? 'text-slate-500' : 'text-zinc-505'
                                    }`}>Model: {asset.model || 'Unknown'}</p>
                                    <span className={`text-[10px] block mt-0.5 transition-colors ${
                                      isLightMode ? 'text-slate-400' : 'text-zinc-600'
                                    }`}>
                                      {formatToIST(asset.created_at)}
                                    </span>
                                  </div>
                                </div>

                                <div className="flex items-center gap-3">
                                  {/* Social status badges */}
                                  <div className="flex items-center gap-1.5">
                                    {asset.posted_insta ? (
                                      <span className="px-2 py-0.5 rounded bg-fuchsia-950/45 border border-fuchsia-900/60 text-fuchsia-400 text-[10px] font-bold">Instagram</span>
                                    ) : (
                                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold transition-colors ${
                                        isLightMode ? 'bg-slate-100 text-slate-400' : 'bg-zinc-900 text-zinc-600'
                                      }`}>Insta Pending</span>
                                    )}
                                    {asset.type === 'video' && (
                                      asset.posted_yt ? (
                                        <span className="px-2 py-0.5 rounded bg-red-950/45 border border-red-900/60 text-red-400 text-[10px] font-bold">YouTube</span>
                                      ) : (
                                        <span className={`px-2 py-0.5 rounded text-[10px] font-semibold transition-colors ${
                                          isLightMode ? 'bg-slate-100 text-slate-400' : 'bg-zinc-900 text-zinc-600'
                                        }`}>YT Pending</span>
                                      )
                                    )}
                                  </div>

                                  {/* Actions */}
                                  <button
                                    onClick={() => handlePreviewMedia(asset, uniqueKey)}
                                    className={`px-3 py-1.5 border rounded-lg text-xs font-semibold transition-all ${
                                      isLightMode 
                                        ? 'bg-slate-50 border-slate-200 hover:bg-slate-100 text-slate-700 hover:text-slate-900 shadow-sm' 
                                        : 'bg-zinc-900 border-zinc-800 hover:border-blue-500/40 hover:text-white'
                                    }`}
                                  >
                                    {signingUrlId === uniqueKey ? 'Refreshing...' : 'Refresh URL'}
                                  </button>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      )}
                    </div>

                    {/* Quick Queue View */}
                    <div className={`backdrop-blur-md border rounded-2xl p-6 flex flex-col transition-all duration-300 ${
                      isLightMode ? 'bg-white border-slate-200 shadow-sm shadow-slate-100/50' : 'bg-zinc-955/40 border-zinc-900'
                    }`}>
                      <div className="flex items-center justify-between mb-5">
                        <h3 className={`font-bold text-base transition-colors ${
                          isLightMode ? 'text-slate-900' : 'text-white'
                        }`}>Generation Queue</h3>
                        <button onClick={() => setActiveTab('queue')} className="text-xs text-blue-600 hover:text-blue-500 font-medium">Manage</button>
                      </div>

                      <div className="space-y-4 flex-1 overflow-y-auto max-h-96 pr-1">
                        <div>
                          <h4 className={`text-xs font-semibold uppercase tracking-wider mb-2.5 transition-colors ${
                            isLightMode ? 'text-slate-450' : 'text-zinc-500'
                          }`}>Images Queue ({imagesQueue.length})</h4>
                          {imagesQueue.length === 0 ? (
                            <div className={`text-xs font-mono py-2 italic transition-colors ${
                              isLightMode ? 'text-slate-400' : 'text-zinc-600'
                            }`}>No pending images in queue.</div>
                          ) : (
                            <div className="space-y-2">
                              {imagesQueue.slice(0, 3).map((item) => (
                                <div key={item.id} className={`p-3 border rounded-xl flex items-center justify-between gap-3 transition-colors ${
                                  isLightMode ? 'bg-slate-50/50 border-slate-150' : 'bg-zinc-900/50 border-zinc-800/80'
                                }`}>
                                  <span className={`text-xs truncate font-mono transition-colors ${
                                    isLightMode ? 'text-slate-700' : 'text-zinc-300'
                                  }`}>{item.prompt}</span>
                                  <span className="px-2 py-0.5 rounded bg-yellow-500/10 text-yellow-500 text-[9px] font-semibold shrink-0 uppercase tracking-widest">Pending</span>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>

                        <div className={`pt-4 border-t transition-colors ${
                          isLightMode ? 'border-slate-100' : 'border-zinc-900'
                        }`}>
                          <h4 className={`text-xs font-semibold uppercase tracking-wider mb-2.5 transition-colors ${
                            isLightMode ? 'text-slate-450' : 'text-zinc-500'
                          }`}>Videos Queue ({videosQueue.length})</h4>
                          {videosQueue.length === 0 ? (
                            <div className={`text-xs font-mono py-2 italic transition-colors ${
                              isLightMode ? 'text-slate-400' : 'text-zinc-600'
                            }`}>No pending videos in queue.</div>
                          ) : (
                            <div className="space-y-2">
                              {videosQueue.slice(0, 3).map((item) => (
                                <div key={item.id} className={`p-3 border rounded-xl flex items-center justify-between gap-3 transition-colors ${
                                  isLightMode ? 'bg-slate-50/50 border-slate-150' : 'bg-zinc-900/50 border-zinc-800/80'
                                }`}>
                                  <span className={`text-xs truncate font-mono transition-colors ${
                                    isLightMode ? 'text-slate-700' : 'text-zinc-300'
                                  }`}>{item.prompt}</span>
                                  <span className="px-2 py-0.5 rounded bg-yellow-500/10 text-yellow-500 text-[9px] font-semibold shrink-0 uppercase tracking-widest">Pending</span>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 2: MEDIA GALLERY */}
              {activeTab === 'media' && (
                <div className="space-y-6">
                  {/* Filters bar */}
                  <div className={`flex flex-col sm:flex-row gap-4 items-center justify-between p-4 border rounded-2xl transition-colors duration-300 ${
                    isLightMode ? 'bg-white border-slate-200/85 shadow-sm shadow-slate-100/50' : 'bg-zinc-955/40 border-zinc-900'
                  }`}>
                    <div className="flex gap-2">
                      <button
                        onClick={() => setMediaFilter('all')}
                        className={`px-4 py-2 text-xs font-bold rounded-xl transition-all ${
                          mediaFilter === 'all' 
                            ? 'bg-blue-600 text-white shadow-sm' 
                            : isLightMode 
                              ? 'bg-slate-100 text-slate-650 hover:text-slate-900' 
                              : 'bg-zinc-900 text-zinc-400 hover:text-white'
                        }`}
                      >
                        All Assets ({mediaAssets.length})
                      </button>
                      <button
                        onClick={() => setMediaFilter('image')}
                        className={`px-4 py-2 text-xs font-bold rounded-xl transition-all ${
                          mediaFilter === 'image' 
                            ? 'bg-blue-600 text-white shadow-sm' 
                            : isLightMode 
                              ? 'bg-slate-100 text-slate-650 hover:text-slate-900' 
                              : 'bg-zinc-900 text-zinc-400 hover:text-white'
                        }`}
                      >
                        Images ({mediaAssets.filter(a => a.type === 'image').length})
                      </button>
                      <button
                        onClick={() => setMediaFilter('video')}
                        className={`px-4 py-2 text-xs font-bold rounded-xl transition-all ${
                          mediaFilter === 'video' 
                            ? 'bg-blue-600 text-white shadow-sm' 
                            : isLightMode 
                              ? 'bg-slate-100 text-slate-650 hover:text-slate-900' 
                              : 'bg-zinc-900 text-zinc-400 hover:text-white'
                        }`}
                      >
                        Videos ({mediaAssets.filter(a => a.type === 'video').length})
                      </button>
                    </div>

                    <div className={`text-xs font-mono transition-colors duration-300 ${
                      isLightMode ? 'text-slate-400' : 'text-zinc-500'
                    }`}>
                      Showing {filteredMedia.length} of {mediaAssets.length} total generated entries
                    </div>
                  </div>

                  {/* Grid outputs */}
                  {filteredMedia.length === 0 ? (
                    <div className={`text-center py-24 border rounded-2xl transition-colors duration-300 ${
                      isLightMode 
                        ? 'bg-white border-slate-200 text-slate-450 shadow-sm shadow-slate-100/50' 
                        : 'bg-zinc-955/20 border-zinc-900 text-zinc-500'
                    }`}>
                      No media files matched the active filters.
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      {filteredMedia.map((asset) => {
                        const uniqueKey = `${asset.type}-${asset.id}`;
                        const previewUrl = activePreviews[uniqueKey] || asset.signed_url;

                        return (
                          <div
                            key={uniqueKey}
                            className={`border rounded-2xl overflow-hidden transition-all duration-300 flex flex-col h-full ${
                              isLightMode 
                                ? 'bg-white border-slate-200 shadow-sm shadow-slate-100/50 hover:border-blue-500/40 hover:shadow-[0_4px_30px_rgba(37,99,235,0.08)]' 
                                : 'bg-zinc-955/45 border-zinc-900 hover:border-blue-500/35 hover:shadow-[0_4px_30px_rgba(37,99,235,0.1)]'
                            }`}
                          >
                            {/* Media content body */}
                            <div className={`aspect-video w-full border-b flex items-center justify-center relative group transition-colors duration-300 ${
                              isLightMode ? 'bg-slate-100 border-slate-200' : 'bg-zinc-900 border-zinc-900'
                            }`}>
                              {previewUrl ? (
                                asset.type === 'image' ? (
                                  // eslint-disable-next-line @next/next/no-img-element
                                  <img 
                                    src={previewUrl} 
                                    alt={asset.alt_text} 
                                    className="w-full h-full object-cover group-hover:scale-[1.03] transition-all duration-700" 
                                  />
                                ) : (
                                  <video 
                                    src={previewUrl} 
                                    controls 
                                    className="w-full h-full object-cover" 
                                  />
                                )
                              ) : (
                                <div className="flex flex-col items-center justify-center text-center p-4">
                                  <div className={`w-14 h-14 rounded-full flex items-center justify-center border text-zinc-500 mb-3 group-hover:text-blue-500 group-hover:border-blue-500/20 transition-all ${
                                    isLightMode ? 'bg-white border-slate-200' : 'bg-zinc-950 border-zinc-800'
                                  }`}>
                                    {asset.type === 'image' ? (
                                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                                        <path strokeLinecap="round" strokeLinejoin="round" d="m2.25 15.75 5.159-5.159a2.25 2.25 0 0 1 3.182 0l5.159 5.159m-1.5-1.5 1.409-1.409a2.25 2.25 0 0 1 3.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 0 0 1.5-1.5V6a1.5 1.5 0 0 0-1.5-1.5H3.75A1.5 1.5 0 0 0 2.25 6v12a1.5 1.5 0 0 0 1.5 1.5Zm10.5-11.25h.008v.008h-.008V8.25Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Z" />
                                      </svg>
                                    ) : (
                                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6 ml-0.5">
                                        <path strokeLinecap="round" strokeLinejoin="round" d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.347a1.125 1.125 0 0 1 0 1.972l-11.54 6.347a1.125 1.125 0 0 1-1.667-.986V5.653Z" />
                                      </svg>
                                    )}
                                  </div>
                                  <span className={`text-[10px] font-mono tracking-wider block mb-2 transition-colors ${
                                    isLightMode ? 'text-slate-400' : 'text-zinc-600'
                                  }`}>{asset.filename || 'No File'}</span>
                                  <span className={`text-xs font-semibold transition-colors ${
                                    isLightMode ? 'text-slate-500' : 'text-zinc-500'
                                  }`}>No Cloud Storage URL</span>
                                </div>
                              )}

                              {previewUrl && (
                                <button
                                  onClick={() => handlePreviewMedia(asset, uniqueKey)}
                                  className={`absolute top-3 right-3 p-2 rounded-xl border transition-all z-10 text-[10px] font-bold ${
                                    isLightMode 
                                      ? 'bg-white/90 hover:bg-white border-slate-200 text-slate-700 shadow-sm' 
                                      : 'bg-zinc-950/80 hover:bg-zinc-950 border-zinc-800 text-zinc-400 hover:text-white'
                                  }`}
                                >
                                  {signingUrlId === uniqueKey ? 'Refreshing...' : 'Refresh URL'}
                                </button>
                              )}
                            </div>

                            {/* Details body */}
                            <div className="p-5 flex-1 flex flex-col justify-between space-y-4">
                              <div className="space-y-2">
                                <span className={`px-2.5 py-0.5 rounded-full border text-[9px] font-mono uppercase tracking-wider inline-block transition-colors ${
                                  isLightMode ? 'bg-slate-50 border-slate-200 text-slate-500' : 'bg-zinc-900 border-zinc-800 text-zinc-400'
                                }`}>
                                  {asset.model || 'Unknown Model'}
                                </span>
                                <h3 className={`font-bold text-sm line-clamp-2 transition-colors duration-300 ${
                                  isLightMode ? 'text-slate-900' : 'text-white'
                                }`} title={asset.prompt}>
                                  {asset.prompt}
                                </h3>
                                {asset.description && (
                                  <p className={`text-xs line-clamp-3 leading-relaxed transition-colors duration-300 ${
                                    isLightMode ? 'text-slate-500' : 'text-zinc-400'
                                  }`}>
                                    {asset.description}
                                  </p>
                                )}
                              </div>

                              <div className={`pt-3 border-t flex items-center justify-between text-[11px] transition-colors duration-300 ${
                                isLightMode ? 'border-slate-100 text-slate-405' : 'border-zinc-900 text-zinc-505'
                              }`}>
                                <span>{formatDateToIST(asset.created_at)}</span>
                                <div className="flex items-center gap-1.5">
                                  {asset.posted_insta ? (
                                    <span className="px-2 py-0.5 rounded bg-fuchsia-950/45 border border-fuchsia-900/45 text-fuchsia-400 font-medium">Insta Shared</span>
                                  ) : (
                                    <span className={`px-2 py-0.5 rounded transition-colors ${
                                      isLightMode ? 'bg-slate-100 text-slate-400' : 'bg-zinc-900 text-zinc-600'
                                    }`}>Insta Off</span>
                                  )}
                                  {asset.type === 'video' && (
                                    asset.posted_yt ? (
                                      <a
                                        href={asset.yt_url}
                                        target="_blank"
                                        rel="noreferrer"
                                        className="px-2 py-0.5 rounded bg-red-950/45 border border-red-900/40 text-red-400 font-medium hover:underline inline-flex items-center gap-0.5"
                                      >
                                        YouTube
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor" className="w-3 h-3">
                                          <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 6H5.25A2.25 2.25 0 0 0 3 8.25v10.5A2.25 2.25 0 0 0 5.25 21h10.5A2.25 2.25 0 0 0 18 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
                                        </svg>
                                      </a>
                                    ) : (
                                      <span className={`px-2 py-0.5 rounded transition-colors ${
                                        isLightMode ? 'bg-slate-100 text-slate-400' : 'bg-zinc-900 text-zinc-600'
                                      }`}>YT Off</span>
                                    )
                                  )}
                                </div>
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              )}

              {/* TAB 3: PIPELINE QUEUE */}
              {activeTab === 'queue' && (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
                    {/* Trigger form */}
                    <div className={`backdrop-blur-md border rounded-2xl p-6 transition-colors duration-300 ${
                      isLightMode ? 'bg-white border-slate-200 shadow-sm shadow-slate-100/50' : 'bg-zinc-955/40 border-zinc-900'
                    }`}>
                      <h3 className={`font-bold text-base mb-5 transition-colors ${
                        isLightMode ? 'text-slate-900' : 'text-white'
                      }`}>Queue New Generation</h3>

                      <form onSubmit={handleAddPrompt} className="space-y-5">
                        <div>
                          <label className={`block text-xs font-semibold uppercase tracking-wider mb-2 transition-colors ${
                            isLightMode ? 'text-slate-500' : 'text-zinc-400'
                          }`}>Asset Type</label>
                          <div className="grid grid-cols-2 gap-2">
                            <button
                              type="button"
                              onClick={() => setNewType('image')}
                              className={`py-2 px-4 rounded-xl text-xs font-bold border transition-all ${
                                newType === 'image'
                                  ? 'bg-blue-600 text-white border-blue-500 shadow-sm'
                                  : isLightMode 
                                    ? 'bg-slate-100 text-slate-600 border-slate-200 hover:text-slate-800' 
                                    : 'bg-zinc-900 text-zinc-400 border-zinc-800 hover:text-white'
                              }`}
                            >
                              Image Prompt
                            </button>
                            <button
                              type="button"
                              onClick={() => setNewType('video')}
                              className={`py-2 px-4 rounded-xl text-xs font-bold border transition-all ${
                                newType === 'video'
                                  ? 'bg-blue-600 text-white border-blue-500 shadow-sm'
                                  : isLightMode 
                                    ? 'bg-slate-100 text-slate-600 border-slate-200 hover:text-slate-800' 
                                    : 'bg-zinc-900 text-zinc-400 border-zinc-800 hover:text-white'
                              }`}
                            >
                              Video Script
                            </button>
                          </div>
                        </div>

                        <div>
                          <label htmlFor="promptInput" className={`block text-xs font-semibold uppercase tracking-wider mb-2 transition-colors ${
                            isLightMode ? 'text-slate-500' : 'text-zinc-400'
                          }`}>Prompt / Deity Name</label>
                          <textarea
                            id="promptInput"
                            rows={3}
                            placeholder="e.g. Shiva, Hanuman, or custom scene details..."
                            value={newPrompt}
                            onChange={(e) => setNewPrompt(e.target.value)}
                            className={`w-full px-4 py-3 border rounded-xl placeholder-zinc-500 focus:outline-none focus:border-blue-500/80 transition-all font-mono text-xs ${
                              isLightMode ? 'bg-slate-50 border-slate-200 text-slate-900' : 'bg-zinc-900/50 border-zinc-800 text-white'
                            }`}
                            required
                          />
                        </div>

                        <div className={`space-y-3 border p-4 rounded-xl transition-colors duration-300 ${
                          isLightMode ? 'bg-slate-50/50 border-slate-150' : 'bg-zinc-900/20 border-zinc-900/50'
                        }`}>
                          <span className={`block text-xs font-semibold uppercase tracking-wider mb-1 transition-colors ${
                            isLightMode ? 'text-slate-450' : 'text-zinc-550'
                          }`}>Post Automation</span>

                          <label className="flex items-center gap-3 cursor-pointer select-none">
                            <input
                              type="checkbox"
                              checked={autoInsta}
                              onChange={(e) => setAutoInsta(e.target.checked)}
                              className="accent-blue-600 rounded"
                            />
                            <span className={`text-xs transition-colors ${
                              isLightMode ? 'text-slate-600' : 'text-zinc-300'
                            }`}>Instagram Feed / Reels publish</span>
                          </label>

                          <label className="flex items-center gap-3 cursor-pointer select-none">
                            <input
                              type="checkbox"
                              checked={autoYt}
                              onChange={(e) => setAutoYt(e.target.checked)}
                              className="accent-blue-600 rounded"
                            />
                            <span className={`text-xs transition-colors ${
                              isLightMode ? 'text-slate-600' : 'text-zinc-300'
                            }`}>YouTube Shorts publish (video only)</span>
                          </label>
                        </div>

                        {submitSuccess && (
                          <div className="p-3 bg-emerald-950/20 border border-emerald-900/50 text-emerald-400 rounded-xl text-xs flex items-center gap-2">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                            Successfully enqueued prompt in Neon Database queue!
                          </div>
                        )}

                        <button
                          type="submit"
                          disabled={submittingPrompt || !newPrompt.trim()}
                          className="w-full py-3 bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white rounded-xl text-xs font-bold transition-all shadow-[0_4px_15px_rgba(37,99,235,0.3)] disabled:opacity-50"
                        >
                          {submittingPrompt ? 'Adding...' : 'Enqueue Generation'}
                        </button>
                      </form>
                    </div>

                    {/* Active Queue lists */}
                    <div className={`backdrop-blur-md border rounded-2xl p-6 transition-colors duration-300 ${
                      isLightMode ? 'bg-white border-slate-200 shadow-sm shadow-slate-100/50' : 'bg-zinc-955/40 border-zinc-900'
                    }`}>
                      <h3 className={`font-bold text-base mb-5 transition-colors ${
                        isLightMode ? 'text-slate-900' : 'text-white'
                      }`}>Pending Pipeline Items</h3>

                      <div className="space-y-6">
                        {/* Images */}
                        <div>
                          <div className="flex items-center justify-between mb-3">
                            <h4 className={`text-xs font-bold uppercase tracking-wider transition-colors ${
                              isLightMode ? 'text-slate-500' : 'text-zinc-400'
                            }`}>Images Generator Queue ({imagesQueue.length})</h4>
                            <span className={`text-[10px] font-mono transition-colors ${
                              isLightMode ? 'text-slate-400' : 'text-zinc-600'
                            }`}>TABLE: images_on_demand</span>
                          </div>

                          {imagesQueue.length === 0 ? (
                            <div className={`text-center py-6 border border-dashed rounded-xl text-xs italic transition-colors duration-300 ${
                              isLightMode ? 'border-slate-200 text-slate-400' : 'border-zinc-900 text-zinc-600'
                            }`}>
                              Queue empty. Use generator form to create entries.
                            </div>
                          ) : (
                            <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                              {imagesQueue.map((item) => (
                                <div key={item.id} className={`p-3 border rounded-xl flex items-center justify-between gap-3 transition-colors ${
                                  isLightMode 
                                    ? 'bg-slate-50/50 border-slate-200 hover:border-slate-305' 
                                    : 'bg-zinc-900/30 border-zinc-900 hover:border-zinc-800'
                                }`}>
                                  <div className="truncate">
                                    <span className={`text-xs font-mono block truncate transition-colors ${
                                      isLightMode ? 'text-slate-700' : 'text-zinc-300'
                                    }`}>{item.prompt}</span>
                                    <span className={`text-[9px] block mt-1 transition-colors ${
                                      isLightMode ? 'text-slate-400' : 'text-zinc-500'
                                    }`}>
                                      Enqueued: {formatToIST(item.created_at)}
                                    </span>
                                  </div>
                                  <div className="flex items-center gap-3 shrink-0">
                                    <span className="px-2 py-0.5 rounded bg-yellow-500/10 text-yellow-505 text-[9px] uppercase tracking-wider font-semibold">Queue</span>
                                    <button
                                      onClick={() => handleDeleteQueueItem('image', item.id)}
                                      className={`p-1 rounded border transition-all ${
                                        isLightMode 
                                          ? 'bg-slate-100 hover:bg-red-50 border-slate-200 hover:border-red-200 text-slate-400 hover:text-red-500' 
                                          : 'bg-zinc-950 hover:bg-red-950 border-zinc-850 hover:border-red-900 text-zinc-500 hover:text-red-400'
                                      }`}
                                      title="Remove from queue"
                                    >
                                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4">
                                        <path strokeLinecap="round" strokeLinejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
                                      </svg>
                                    </button>
                                  </div>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>

                        {/* Videos */}
                        <div className={`pt-4 border-t transition-colors ${
                          isLightMode ? 'border-slate-100' : 'border-zinc-900'
                        }`}>
                          <div className="flex items-center justify-between mb-3">
                            <h4 className={`text-xs font-bold uppercase tracking-wider transition-colors ${
                              isLightMode ? 'text-slate-500' : 'text-zinc-400'
                            }`}>Videos Generator Queue ({videosQueue.length})</h4>
                            <span className={`text-[10px] font-mono transition-colors ${
                              isLightMode ? 'text-slate-400' : 'text-zinc-600'
                            }`}>TABLE: videos_on_demand</span>
                          </div>

                          {videosQueue.length === 0 ? (
                            <div className={`text-center py-6 border border-dashed rounded-xl text-xs italic transition-colors duration-300 ${
                              isLightMode ? 'border-slate-200 text-slate-400' : 'border-zinc-900 text-zinc-600'
                            }`}>
                              Queue empty. Use generator form to create entries.
                            </div>
                          ) : (
                            <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                              {videosQueue.map((item) => (
                                <div key={item.id} className={`p-3 border rounded-xl flex items-center justify-between gap-3 transition-colors ${
                                  isLightMode 
                                    ? 'bg-slate-50/50 border-slate-200 hover:border-slate-305' 
                                    : 'bg-zinc-900/30 border-zinc-900 hover:border-zinc-800'
                                }`}>
                                  <div className="truncate">
                                    <span className={`text-xs font-mono block truncate transition-colors ${
                                      isLightMode ? 'text-slate-700' : 'text-zinc-300'
                                    }`}>{item.prompt}</span>
                                    <span className={`text-[9px] block mt-1 transition-colors ${
                                      isLightMode ? 'text-slate-400' : 'text-zinc-500'
                                    }`}>
                                      Enqueued: {formatToIST(item.created_at)}
                                    </span>
                                  </div>
                                  <div className="flex items-center gap-3 shrink-0">
                                    <span className="px-2 py-0.5 rounded bg-yellow-500/10 text-yellow-505 text-[9px] uppercase tracking-wider font-semibold">Queue</span>
                                    <button
                                      onClick={() => handleDeleteQueueItem('video', item.id)}
                                      className={`p-1 rounded border transition-all ${
                                        isLightMode 
                                          ? 'bg-slate-100 hover:bg-red-50 border-slate-200 hover:border-red-200 text-slate-400 hover:text-red-500' 
                                          : 'bg-zinc-950 hover:bg-red-950 border-zinc-850 hover:border-red-900 text-zinc-500 hover:text-red-400'
                                      }`}
                                      title="Remove from queue"
                                    >
                                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4">
                                        <path strokeLinecap="round" strokeLinejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
                                      </svg>
                                    </button>
                                  </div>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 4: GCS STORAGE EXPLORER */}
              {activeTab === 'storage' && (
                <div className="space-y-6">
                  <div className={`backdrop-blur-md border rounded-2xl overflow-hidden transition-colors duration-300 ${
                    isLightMode ? 'bg-white border-slate-200 shadow-sm shadow-slate-100/50' : 'bg-zinc-955/40 border-zinc-900'
                  }`}>
                    <div className={`px-6 py-5 border-b flex flex-col sm:flex-row gap-4 items-center justify-between transition-colors duration-300 ${
                      isLightMode ? 'border-slate-200' : 'border-zinc-900'
                    }`}>
                      <div>
                        <h3 className={`font-bold text-base transition-colors ${
                          isLightMode ? 'text-slate-900' : 'text-white'
                        }`}>Google Cloud Storage bucket explorer</h3>
                        <p className={`text-xs mt-1 font-mono transition-colors ${
                          isLightMode ? 'text-slate-400' : 'text-zinc-550'
                        }`}>Bucket: databucket_reels_photos</p>
                      </div>

                      <div className={`text-xs font-mono transition-colors ${
                        isLightMode ? 'text-slate-500' : 'text-zinc-400'
                      }`}>
                        Objects listed: {gcsFiles.length} files
                      </div>
                    </div>

                    {gcsFiles.length === 0 ? (
                      <div className="text-center py-20 text-zinc-500 text-sm font-mono">No files found inside the GCS bucket.</div>
                    ) : (
                      <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                          <thead>
                            <tr className={`border-b text-xs font-semibold uppercase font-mono tracking-wider transition-colors duration-300 ${
                              isLightMode 
                                ? 'border-slate-200 bg-slate-50 text-slate-500' 
                                : 'border-zinc-900 bg-zinc-950/30 text-zinc-400'
                            }`}>
                              <th className="py-4 px-6">Name</th>
                              <th className="py-4 px-6">Content Type</th>
                              <th className="py-4 px-6">Size</th>
                              <th className="py-4 px-6">Updated At</th>
                              <th className="py-4 px-6 text-right">Preview Actions</th>
                            </tr>
                          </thead>
                          <tbody className={`divide-y text-sm transition-colors duration-300 ${
                            isLightMode ? 'divide-slate-100' : 'divide-zinc-900'
                          }`}>
                            {gcsFiles.map((file) => {
                              const uniqueKey = `gcs-${file.name}`;
                              const isPreviewing = !!activePreviews[uniqueKey];
                              const previewUrl = activePreviews[uniqueKey];

                              return (
                                <React.Fragment key={file.id || file.name}>
                                  <tr className={`transition-all ${
                                    isLightMode ? 'hover:bg-slate-50/50' : 'hover:bg-zinc-900/20'
                                  }`}>
                                    <td className={`py-4 px-6 font-mono text-xs max-w-xs truncate transition-colors ${
                                      isLightMode ? 'text-slate-700' : 'text-zinc-300'
                                    }`} title={file.name}>
                                      {file.name}
                                    </td>
                                    <td className={`py-4 px-6 font-mono text-xs transition-colors ${
                                      isLightMode ? 'text-slate-400 font-medium' : 'text-zinc-500'
                                    }`}>
                                      {file.contentType}
                                    </td>
                                    <td className={`py-4 px-6 font-mono text-xs transition-colors ${
                                      isLightMode ? 'text-slate-500' : 'text-zinc-400'
                                    }`}>
                                      {formatBytes(file.size)}
                                    </td>
                                    <td className={`py-4 px-6 text-xs transition-colors ${
                                      isLightMode ? 'text-slate-500 font-medium' : 'text-zinc-500'
                                    }`}>
                                      {formatToIST(file.updated)}
                                    </td>
                                    <td className="py-4 px-6 text-right">
                                      <div className="flex items-center justify-end gap-2">
                                        <button
                                          onClick={() => handlePreviewMedia(file.name, uniqueKey)}
                                          className={`px-3 py-1.5 border rounded-lg text-xs font-semibold transition-all ${
                                            isLightMode 
                                              ? 'bg-slate-50 hover:bg-slate-100 border-slate-200 text-slate-700 hover:text-slate-900 shadow-sm' 
                                              : 'bg-zinc-900 hover:bg-zinc-800 border-zinc-800 text-zinc-300 hover:text-white'
                                          }`}
                                        >
                                          {signingUrlId === uniqueKey ? 'Signing...' : isPreviewing ? 'Hide' : 'Reveal Link'}
                                        </button>

                                        {isPreviewing && previewUrl && (
                                          <a
                                            href={previewUrl}
                                            target="_blank"
                                            rel="noreferrer"
                                            className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 rounded-lg text-xs font-semibold text-white transition-all inline-flex items-center gap-1"
                                          >
                                            Open
                                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor" className="w-3.5 h-3.5">
                                              <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 6H5.25A2.25 2.25 0 0 0 3 8.25v10.5A2.25 2.25 0 0 0 5.25 21h10.5A2.25 2.25 0 0 0 18 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
                                            </svg>
                                          </a>
                                        )}
                                      </div>
                                    </td>
                                  </tr>

                                  {isPreviewing && previewUrl && (
                                    <tr className={isLightMode ? 'bg-slate-50/20' : 'bg-zinc-955/40'}>
                                      <td colSpan={5} className={`py-4 px-6 border-b transition-colors duration-305 ${
                                        isLightMode ? 'border-slate-100' : 'border-zinc-900'
                                      }`}>
                                        <div className={`max-w-xl mx-auto rounded-xl overflow-hidden border shadow-inner flex items-center justify-center p-3 relative transition-colors duration-300 ${
                                          isLightMode ? 'bg-slate-50 border-slate-200' : 'bg-zinc-950 border-zinc-850'
                                        }`}>
                                          {file.contentType.startsWith('image/') ? (
                                            // eslint-disable-next-line @next/next/no-img-element
                                            <img src={previewUrl} alt={file.name} className="max-h-64 object-contain rounded" />
                                          ) : file.contentType.startsWith('video/') ? (
                                            <video src={previewUrl} controls className="max-h-64 object-contain rounded w-full" />
                                          ) : (
                                            <div className={`p-8 text-center font-mono text-xs transition-colors duration-300 ${
                                              isLightMode ? 'text-slate-550' : 'text-zinc-550'
                                            }`}>
                                              No preview available for content type: {file.contentType}
                                              <div className="mt-3">
                                                <a href={previewUrl} download className="text-blue-605 hover:underline">Download file directly</a>
                                              </div>
                                            </div>
                                          )}
                                        </div>
                                      </td>
                                    </tr>
                                  )}
                                </React.Fragment>
                              );
                            })}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* TAB 5: ANALYTICS */}
              {activeTab === 'analytics' && (
                <div className="space-y-6">
                  {/* Aggregated totals widgets */}
                  <div className="grid grid-cols-2 lg:grid-cols-6 gap-4">
                    <div className={`p-4 border rounded-xl transition-all duration-300 ${
                      isLightMode ? 'bg-white border-slate-200 shadow-sm' : 'bg-zinc-900/40 border-zinc-800'
                    }`}>
                      <span className={`text-[10px] font-semibold uppercase tracking-wider block transition-colors ${
                        isLightMode ? 'text-slate-400' : 'text-zinc-500'
                      }`}>Total Impressions</span>
                      <span className={`text-xl font-bold mt-1 block transition-colors ${
                        isLightMode ? 'text-slate-900' : 'text-white'
                      }`}>{analytics.sums.impressions.toLocaleString()}</span>
                    </div>
                    <div className={`p-4 border rounded-xl transition-all duration-300 ${
                      isLightMode ? 'bg-white border-slate-200 shadow-sm' : 'bg-zinc-900/40 border-zinc-800'
                    }`}>
                      <span className={`text-[10px] font-semibold uppercase tracking-wider block transition-colors ${
                        isLightMode ? 'text-slate-400' : 'text-zinc-500'
                      }`}>Total Reach</span>
                      <span className={`text-xl font-bold mt-1 block transition-colors ${
                        isLightMode ? 'text-slate-900' : 'text-white'
                      }`}>{analytics.sums.reach.toLocaleString()}</span>
                    </div>
                    <div className={`p-4 border rounded-xl transition-all duration-300 ${
                      isLightMode ? 'bg-white border-slate-200 shadow-sm' : 'bg-zinc-900/40 border-zinc-800'
                    }`}>
                      <span className={`text-[10px] font-semibold uppercase tracking-wider block transition-colors ${
                        isLightMode ? 'text-slate-400' : 'text-zinc-500'
                      }`}>Total Likes</span>
                      <span className={`text-xl font-bold mt-1 block transition-colors ${
                        isLightMode ? 'text-slate-900' : 'text-white'
                      }`}>{analytics.sums.likes.toLocaleString()}</span>
                    </div>
                    <div className={`p-4 border rounded-xl transition-all duration-300 ${
                      isLightMode ? 'bg-white border-slate-200 shadow-sm' : 'bg-zinc-900/40 border-zinc-800'
                    }`}>
                      <span className={`text-[10px] font-semibold uppercase tracking-wider block transition-colors ${
                        isLightMode ? 'text-slate-400' : 'text-zinc-500'
                      }`}>Total Comments</span>
                      <span className={`text-xl font-bold mt-1 block transition-colors ${
                        isLightMode ? 'text-slate-900' : 'text-white'
                      }`}>{analytics.sums.comments.toLocaleString()}</span>
                    </div>
                    <div className={`p-4 border rounded-xl transition-all duration-300 ${
                      isLightMode ? 'bg-white border-slate-200 shadow-sm' : 'bg-zinc-900/40 border-zinc-800'
                    }`}>
                      <span className={`text-[10px] font-semibold uppercase tracking-wider block transition-colors ${
                        isLightMode ? 'text-slate-400' : 'text-zinc-500'
                      }`}>Total Shares</span>
                      <span className={`text-xl font-bold mt-1 block transition-colors ${
                        isLightMode ? 'text-slate-900' : 'text-white'
                      }`}>{analytics.sums.shares.toLocaleString()}</span>
                    </div>
                    <div className={`p-4 border rounded-xl transition-all duration-300 ${
                      isLightMode ? 'bg-white border-slate-200 shadow-sm' : 'bg-zinc-900/40 border-zinc-800'
                    }`}>
                      <span className={`text-[10px] font-semibold uppercase tracking-wider block transition-colors ${
                        isLightMode ? 'text-slate-400' : 'text-zinc-500'
                      }`}>Total Saves</span>
                      <span className={`text-xl font-bold mt-1 block transition-colors ${
                        isLightMode ? 'text-slate-900' : 'text-white'
                      }`}>{analytics.sums.saves.toLocaleString()}</span>
                    </div>
                  </div>

                  {/* SVG Interactions Chart */}
                  <div className={`backdrop-blur-md border rounded-2xl p-6 transition-all duration-300 ${
                    isLightMode ? 'bg-white border-slate-200 shadow-sm shadow-slate-100/50' : 'bg-zinc-955/40 border-zinc-900'
                  }`}>
                    <h3 className={`font-bold text-base mb-6 transition-colors ${
                      isLightMode ? 'text-slate-900' : 'text-white'
                    }`}>Interaction Analytics Visualization</h3>

                    {/* Dynamic custom SVG bar chart */}
                    <div className={`w-full aspect-[21/9] rounded-xl p-4 border flex flex-col justify-between transition-colors duration-300 ${
                      isLightMode ? 'bg-slate-50 border-slate-200/80' : 'bg-zinc-955/40 border-zinc-900'
                    }`}>
                      {/* SVG Canvas */}
                      <div className="w-full flex-1 flex items-end gap-6 relative pt-6 px-4">
                        {/* Grid lines */}
                        <div className={`absolute inset-x-0 bottom-0 top-6 border-b flex flex-col justify-between pointer-events-none transition-colors duration-300 ${
                          isLightMode ? 'border-slate-200/50' : 'border-zinc-900'
                        }`}>
                          <div className={`w-full border-t ${isLightMode ? 'border-slate-200/20' : 'border-zinc-900/20'}`} />
                          <div className={`w-full border-t ${isLightMode ? 'border-slate-200/25' : 'border-zinc-900/25'}`} />
                          <div className={`w-full border-t ${isLightMode ? 'border-slate-200/35' : 'border-zinc-900/35'}`} />
                          <div className={`w-full border-t ${isLightMode ? 'border-slate-200/50' : 'border-zinc-900/50'}`} />
                        </div>

                        {/* Impressions Bar */}
                        <div className="flex-1 flex flex-col items-center justify-end h-full gap-2 relative z-10 group">
                          <div className="w-full max-w-[80px] bg-gradient-to-t from-blue-600/80 to-blue-500 rounded-t-lg transition-all duration-500 hover:opacity-90 shadow-[0_0_15px_rgba(37,99,235,0.3)]" style={{ height: '70%' }}>
                            <div className={`absolute -top-6 left-1/2 -translate-x-1/2 px-2 py-0.5 rounded border text-[10px] opacity-0 group-hover:opacity-100 transition-all font-mono pointer-events-none ${
                              isLightMode ? 'bg-white border-slate-200 text-slate-700 shadow-sm shadow-slate-100/50' : 'bg-zinc-900 border-zinc-800 text-zinc-300'
                            }`}>
                              {analytics.sums.impressions}
                            </div>
                          </div>
                          <span className={`text-[10px] font-mono transition-colors ${
                            isLightMode ? 'text-slate-400' : 'text-zinc-500'
                          }`}>Impressions</span>
                        </div>

                        {/* Reach Bar */}
                        <div className="flex-1 flex flex-col items-center justify-end h-full gap-2 relative z-10 group">
                          <div className="w-full max-w-[80px] bg-gradient-to-t from-cyan-600/80 to-cyan-500 rounded-t-lg transition-all duration-500 hover:opacity-90 shadow-[0_0_15px_rgba(6,182,212,0.3)]" style={{ height: '55%' }}>
                            <div className={`absolute -top-6 left-1/2 -translate-x-1/2 px-2 py-0.5 rounded border text-[10px] opacity-0 group-hover:opacity-100 transition-all font-mono pointer-events-none ${
                              isLightMode ? 'bg-white border-slate-200 text-slate-700 shadow-sm shadow-slate-100/50' : 'bg-zinc-900 border-zinc-800 text-zinc-300'
                            }`}>
                              {analytics.sums.reach}
                            </div>
                          </div>
                          <span className={`text-[10px] font-mono transition-colors ${
                            isLightMode ? 'text-slate-400' : 'text-zinc-500'
                          }`}>Reach</span>
                        </div>

                        {/* Likes Bar */}
                        <div className="flex-1 flex flex-col items-center justify-end h-full gap-2 relative z-10 group">
                          <div className="w-full max-w-[80px] bg-gradient-to-t from-rose-600/80 to-rose-500 rounded-t-lg transition-all duration-500 hover:opacity-90 shadow-[0_0_15px_rgba(244,63,94,0.3)]" style={{ height: '40%' }}>
                            <div className={`absolute -top-6 left-1/2 -translate-x-1/2 px-2 py-0.5 rounded border text-[10px] opacity-0 group-hover:opacity-100 transition-all font-mono pointer-events-none ${
                              isLightMode ? 'bg-white border-slate-200 text-slate-700 shadow-sm shadow-slate-100/50' : 'bg-zinc-900 border-zinc-800 text-zinc-300'
                            }`}>
                              {analytics.sums.likes}
                            </div>
                          </div>
                          <span className={`text-[10px] font-mono transition-colors ${
                            isLightMode ? 'text-slate-400' : 'text-zinc-500'
                          }`}>Likes</span>
                        </div>

                        {/* Comments Bar */}
                        <div className="flex-1 flex flex-col items-center justify-end h-full gap-2 relative z-10 group">
                          <div className="w-full max-w-[80px] bg-gradient-to-t from-amber-600/80 to-amber-500 rounded-t-lg transition-all duration-500 hover:opacity-90 shadow-[0_0_15px_rgba(245,158,11,0.3)]" style={{ height: '25%' }}>
                            <div className={`absolute -top-6 left-1/2 -translate-x-1/2 px-2 py-0.5 rounded border text-[10px] opacity-0 group-hover:opacity-100 transition-all font-mono pointer-events-none ${
                              isLightMode ? 'bg-white border-slate-200 text-slate-700 shadow-sm shadow-slate-100/50' : 'bg-zinc-900 border-zinc-800 text-zinc-300'
                            }`}>
                              {analytics.sums.comments}
                            </div>
                          </div>
                          <span className={`text-[10px] font-mono transition-colors ${
                            isLightMode ? 'text-slate-400' : 'text-zinc-500'
                          }`}>Comments</span>
                        </div>

                        {/* Shares Bar */}
                        <div className="flex-1 flex flex-col items-center justify-end h-full gap-2 relative z-10 group">
                          <div className="w-full max-w-[80px] bg-gradient-to-t from-fuchsia-600/80 to-fuchsia-500 rounded-t-lg transition-all duration-500 hover:opacity-90 shadow-[0_0_15px_rgba(217,70,239,0.3)]" style={{ height: '18%' }}>
                            <div className={`absolute -top-6 left-1/2 -translate-x-1/2 px-2 py-0.5 rounded border text-[10px] opacity-0 group-hover:opacity-100 transition-all font-mono pointer-events-none ${
                              isLightMode ? 'bg-white border-slate-200 text-slate-700 shadow-sm shadow-slate-100/50' : 'bg-zinc-900 border-zinc-800 text-zinc-300'
                            }`}>
                              {analytics.sums.shares}
                            </div>
                          </div>
                          <span className={`text-[10px] font-mono transition-colors ${
                            isLightMode ? 'text-slate-400' : 'text-zinc-500'
                          }`}>Shares</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </main>
      </div>
    </div>
  );
}
