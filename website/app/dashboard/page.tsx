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
    <div className="flex h-screen bg-[#090b16] text-zinc-100 overflow-hidden font-sans">
      {/* Dynamic Glow Orbs */}
      <div className="absolute top-0 right-0 w-[400px] h-[400px] rounded-full bg-violet-900/10 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-[500px] h-[500px] rounded-full bg-cyan-900/10 blur-[150px] pointer-events-none" />

      {/* Sidebar - Mobile Toggle */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-zinc-950/80 border-r border-zinc-900 backdrop-blur-md transform transition-transform duration-300 md:relative md:translate-x-0
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
      `}>
        <div className="flex flex-col h-full">
          {/* Logo Section */}
          <div className="flex items-center gap-3 px-6 py-6 border-b border-zinc-900">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-violet-600 to-fuchsia-500 flex items-center justify-center shadow-[0_0_15px_rgba(139,92,246,0.4)]">
              <span className="text-white font-black text-lg">AG</span>
            </div>
            <div>
              <h2 className="font-bold text-white tracking-tight leading-none text-base">Synaptic Flow</h2>
              <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest mt-1 inline-block">Post Control</span>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto">
            <button
              onClick={() => { setActiveTab('overview'); setSidebarOpen(false); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${activeTab === 'overview'
                  ? 'bg-violet-600/15 text-violet-400 border border-violet-500/20 shadow-[0_0_15px_-3px_rgba(139,92,246,0.25)]'
                  : 'text-zinc-400 hover:text-zinc-100 hover:bg-zinc-900/40 border border-transparent'
                }`}
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5">
                <path strokeLinecap="round" strokeLinejoin="round" d="m2.25 12 8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" />
              </svg>
              Overview
            </button>

            <button
              onClick={() => { setActiveTab('media'); setSidebarOpen(false); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${activeTab === 'media'
                  ? 'bg-violet-600/15 text-violet-400 border border-violet-500/20 shadow-[0_0_15px_-3px_rgba(139,92,246,0.25)]'
                  : 'text-zinc-400 hover:text-zinc-100 hover:bg-zinc-900/40 border border-transparent'
                }`}
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5">
                <path strokeLinecap="round" strokeLinejoin="round" d="m2.25 15.75 5.159-5.159a2.25 2.25 0 0 1 3.182 0l5.159 5.159m-1.5-1.5 1.409-1.409a2.25 2.25 0 0 1 3.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 0 0 1.5-1.5V6a1.5 1.5 0 0 0-1.5-1.5H3.75A1.5 1.5 0 0 0 2.25 6v12a1.5 1.5 0 0 0 1.5 1.5Zm10.5-11.25h.008v.008h-.008V8.25Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Z" />
              </svg>
              Media Gallery
            </button>

            <button
              onClick={() => { setActiveTab('queue'); setSidebarOpen(false); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${activeTab === 'queue'
                  ? 'bg-violet-600/15 text-violet-400 border border-violet-500/20 shadow-[0_0_15px_-3px_rgba(139,92,246,0.25)]'
                  : 'text-zinc-400 hover:text-zinc-100 hover:bg-zinc-900/40 border border-transparent'
                }`}
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 12h16.5m-16.5 3.75h16.5M3.75 19.5h16.5M5.625 4.5h12.75c.621 0 1.125.504 1.125 1.125v1.875c0 .621-.504 1.125-1.125 1.125H5.625A1.125 1.125 0 0 1 4.5 7.5V5.625c0-.621.504-1.125 1.125-1.125Z" />
              </svg>
              Pipeline Queue
              {(imagesQueue.length + videosQueue.length) > 0 && (
                <span className="ml-auto px-2 py-0.5 text-xs font-bold rounded-full bg-violet-600 text-white animate-pulse">
                  {imagesQueue.length + videosQueue.length}
                </span>
              )}
            </button>

            <button
              onClick={() => { setActiveTab('storage'); setSidebarOpen(false); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${activeTab === 'storage'
                  ? 'bg-violet-600/15 text-violet-400 border border-violet-500/20 shadow-[0_0_15px_-3px_rgba(139,92,246,0.25)]'
                  : 'text-zinc-400 hover:text-zinc-100 hover:bg-zinc-900/40 border border-transparent'
                }`}
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 7.5l-.625 10.632a2.25 2.25 0 0 1-2.247 2.118H6.622a2.25 2.25 0 0 1-2.247-2.118L3.75 7.5M10 11.25h4M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z" />
              </svg>
              GCS Bucket Files
            </button>

            <button
              onClick={() => { setActiveTab('analytics'); setSidebarOpen(false); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${activeTab === 'analytics'
                  ? 'bg-violet-600/15 text-violet-400 border border-violet-500/20 shadow-[0_0_15px_-3px_rgba(139,92,246,0.25)]'
                  : 'text-zinc-400 hover:text-zinc-100 hover:bg-zinc-900/40 border border-transparent'
                }`}
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 6a7.5 7.5 0 1 0 7.5 7.5h-7.5V6Z" />
                <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 10.5H21A7.5 7.5 0 0 0 13.5 3v7.5Z" />
              </svg>
              Analytics
            </button>
          </nav>

          {/* User Settings & Logout */}
          <div className="p-4 border-t border-zinc-900">
            <button
              onClick={handleLogout}
              className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-xs font-semibold text-zinc-400 hover:text-white hover:bg-red-950/25 border border-transparent hover:border-red-900/30 transition-all"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4.5 h-4.5 text-zinc-500">
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
        <header className="flex items-center justify-between px-6 py-4 bg-zinc-950/50 border-b border-zinc-900 backdrop-blur-md">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(true)}
              className="p-2 -ml-2 text-zinc-400 hover:text-white md:hidden"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-6 h-6">
                <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
              </svg>
            </button>
            <h1 className="text-lg font-bold text-white capitalize tracking-wide">
              {activeTab} Management
            </h1>
          </div>

          <div className="flex items-center gap-4">
            {/* Sync Refresh Button */}
            <button
              onClick={fetchData}
              disabled={loading}
              className="p-2 rounded-xl text-zinc-400 hover:text-white hover:bg-zinc-900/50 border border-zinc-800 disabled:opacity-50 transition-all"
              title="Sync Dashboard Data"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99" />
              </svg>
            </button>
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-950/20 border border-emerald-900/40 text-emerald-400 text-xs font-medium">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
              Connected to Neon DB
            </div>
          </div>
        </header>

        {/* Dashboard Panels Wrapper */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8 space-y-6">
          {errorMsg && (
            <div className="p-4 bg-red-950/25 border border-red-900/40 rounded-xl text-red-300 text-sm flex items-center justify-between">
              <span className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-red-500" />
                {errorMsg}
              </span>
              <button onClick={() => setErrorMsg('')} className="text-zinc-500 hover:text-white">Dismiss</button>
            </div>
          )}

          {loading && mediaAssets.length === 0 ? (
            <div className="h-64 flex flex-col items-center justify-center gap-4">
              <svg className="animate-spin h-10 w-10 text-violet-500" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              <span className="text-zinc-400 font-mono text-sm">Syncing Cloud Assets...</span>
            </div>
          ) : (
            <>
              {/* TAB 1: OVERVIEW */}
              {activeTab === 'overview' && (
                <div className="space-y-6">
                  {/* Project Banner Display */}
                  <div className="relative w-full h-[180px] rounded-2xl overflow-hidden border border-zinc-800/80 shadow-xl">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src="/project_banner.png"
                      alt="Project Banner"
                      className="w-full h-full object-cover"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-[#090b16] via-[#090b16]/30 to-transparent" />
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
                    <div className="backdrop-blur-md bg-zinc-900/40 border border-zinc-800/80 p-5 rounded-2xl flex items-center justify-between hover:border-violet-500/25 transition-all">
                      <div>
                        <span className="text-zinc-500 text-xs font-semibold uppercase tracking-wider block">Images Generated</span>
                        <span className="text-3xl font-extrabold text-white mt-1.5 block">{analytics.counts.images}</span>
                      </div>
                      <div className="w-12 h-12 rounded-xl bg-violet-600/10 border border-violet-500/20 flex items-center justify-center text-violet-400">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-6 h-6">
                          <path strokeLinecap="round" strokeLinejoin="round" d="m2.25 15.75 5.159-5.159a2.25 2.25 0 0 1 3.182 0l5.159 5.159m-1.5-1.5 1.409-1.409a2.25 2.25 0 0 1 3.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 0 0 1.5-1.5V6a1.5 1.5 0 0 0-1.5-1.5H3.75A1.5 1.5 0 0 0 2.25 6v12a1.5 1.5 0 0 0 1.5 1.5Zm10.5-11.25h.008v.008h-.008V8.25Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Z" />
                        </svg>
                      </div>
                    </div>

                    {/* Widget 2 */}
                    <div className="backdrop-blur-md bg-zinc-900/40 border border-zinc-800/80 p-5 rounded-2xl flex items-center justify-between hover:border-cyan-500/25 transition-all">
                      <div>
                        <span className="text-zinc-500 text-xs font-semibold uppercase tracking-wider block">Videos Generated</span>
                        <span className="text-3xl font-extrabold text-white mt-1.5 block">{analytics.counts.videos}</span>
                      </div>
                      <div className="w-12 h-12 rounded-xl bg-cyan-600/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-6 h-6">
                          <path strokeLinecap="round" strokeLinejoin="round" d="m15.75 10.5 4.72-4.72a.75.75 0 0 1 1.28.53v11.38a.75.75 0 0 1-1.28.53l-4.72-4.72M4.5 18.75h9a2.25 2.25 0 0 0 2.25-2.25v-9a2.25 2.25 0 0 0-2.25-2.25h-9A2.25 2.25 0 0 0 2.25 7.5v9a2.25 2.25 0 0 0 2.25 2.25Z" />
                        </svg>
                      </div>
                    </div>

                    {/* Widget 3 */}
                    <div className="backdrop-blur-md bg-zinc-900/40 border border-zinc-800/80 p-5 rounded-2xl flex items-center justify-between hover:border-yellow-500/25 transition-all">
                      <div>
                        <span className="text-zinc-500 text-xs font-semibold uppercase tracking-wider block">Queued Prompts</span>
                        <span className="text-3xl font-extrabold text-white mt-1.5 block">
                          {analytics.counts.imagesQueue + analytics.counts.videosQueue}
                        </span>
                      </div>
                      <div className="w-12 h-12 rounded-xl bg-yellow-600/10 border border-yellow-500/20 flex items-center justify-center text-yellow-400">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-6 h-6">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
                        </svg>
                      </div>
                    </div>

                    {/* Widget 4 */}
                    <div className="backdrop-blur-md bg-zinc-900/40 border border-zinc-800/80 p-5 rounded-2xl flex items-center justify-between hover:border-emerald-500/25 transition-all">
                      <div>
                        <span className="text-zinc-500 text-xs font-semibold uppercase tracking-wider block">Instagram Shares</span>
                        <span className="text-3xl font-extrabold text-white mt-1.5 block">
                          {analytics.counts.postedInstaImages + analytics.counts.postedInstaVideos}
                        </span>
                      </div>
                      <div className="w-12 h-12 rounded-xl bg-emerald-600/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-6 h-6">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M7.217 10.907a2.25 2.25 0 100 2.186m0-2.186l9.566-5.314m-9.566 7.5l9.566 5.314m0 0a2.25 2.25 0 103.935 2.186 2.25 2.25 0 0 0-3.935-2.186zm0-12.814a2.25 2.25 0 103.933-2.185 2.25 2.25 0 0 0-3.933 2.185z" />
                        </svg>
                      </div>
                    </div>
                  </div>

                  {/* Main Grid: Latest Release Feed + Queue Quick View */}
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Latest Release feed */}
                    <div className="lg:col-span-2 backdrop-blur-md bg-zinc-950/40 border border-zinc-900 rounded-2xl p-6">
                      <div className="flex items-center justify-between mb-5">
                        <h3 className="font-bold text-white text-base">Latest Media Outputs</h3>
                        <button onClick={() => setActiveTab('media')} className="text-xs text-violet-400 hover:text-violet-300 font-medium">View All</button>
                      </div>

                      {mediaAssets.length === 0 ? (
                        <div className="text-center py-12 text-zinc-500 text-sm font-mono">No outputs found in the database yet.</div>
                      ) : (
                        <div className="divide-y divide-zinc-900">
                          {mediaAssets.slice(0, 5).map((asset) => {
                            const uniqueKey = `${asset.type}-${asset.id}`;
                            const isPreviewing = !!activePreviews[uniqueKey];
                            const previewUrl = activePreviews[uniqueKey];

                            return (
                              <div key={uniqueKey} className="py-4 first:pt-0 last:pb-0 flex flex-col md:flex-row gap-4 items-start justify-between">
                                <div className="flex gap-4">
                                  {/* Thumbnail Preview Area */}
                                  <div className="relative w-16 h-16 rounded-xl bg-zinc-900 border border-zinc-800 flex-shrink-0 overflow-hidden flex items-center justify-center">
                                    {isPreviewing && previewUrl ? (
                                      asset.type === 'image' ? (
                                        // eslint-disable-next-line @next/next/no-img-element
                                        <img src={previewUrl} alt={asset.alt_text} className="object-cover w-full h-full" />
                                      ) : (
                                        <video src={previewUrl} className="object-cover w-full h-full" muted />
                                      )
                                    ) : (
                                      <div className="flex flex-col items-center justify-center text-[10px] text-zinc-600 font-mono">
                                        <span>{asset.type.toUpperCase()}</span>
                                      </div>
                                    )}
                                  </div>

                                  <div>
                                    <h4 className="font-semibold text-white text-sm line-clamp-1">{asset.prompt}</h4>
                                    <p className="text-xs text-zinc-500 font-mono mt-1">Model: {asset.model || 'Unknown'}</p>
                                    <span className="text-[10px] text-zinc-600 block mt-0.5">
                                      {new Date(asset.created_at).toLocaleString()}
                                    </span>
                                  </div>
                                </div>

                                <div className="flex items-center gap-3">
                                  {/* Social status badges */}
                                  <div className="flex items-center gap-1.5">
                                    {asset.posted_insta ? (
                                      <span className="px-2 py-0.5 rounded bg-fuchsia-950/45 border border-fuchsia-900/60 text-fuchsia-400 text-[10px] font-bold">Instagram</span>
                                    ) : (
                                      <span className="px-2 py-0.5 rounded bg-zinc-900 text-zinc-600 text-[10px] font-semibold">Insta Pending</span>
                                    )}
                                    {asset.type === 'video' && (
                                      asset.posted_yt ? (
                                        <span className="px-2 py-0.5 rounded bg-red-950/45 border border-red-900/60 text-red-400 text-[10px] font-bold">YouTube</span>
                                      ) : (
                                        <span className="px-2 py-0.5 rounded bg-zinc-900 text-zinc-600 text-[10px] font-semibold">YT Pending</span>
                                      )
                                    )}
                                  </div>

                                  {/* Actions */}
                                  <button
                                    onClick={() => handlePreviewMedia(asset, uniqueKey)}
                                    className="px-3 py-1.5 bg-zinc-900 border border-zinc-800 hover:border-violet-500/40 rounded-lg text-xs font-semibold hover:text-white transition-all"
                                  >
                                    {signingUrlId === uniqueKey ? 'Generating...' : isPreviewing ? 'Hide' : 'Reveal'}
                                  </button>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      )}
                    </div>

                    {/* Quick Queue View */}
                    <div className="backdrop-blur-md bg-zinc-950/40 border border-zinc-900 rounded-2xl p-6 flex flex-col">
                      <div className="flex items-center justify-between mb-5">
                        <h3 className="font-bold text-white text-base">Generation Queue</h3>
                        <button onClick={() => setActiveTab('queue')} className="text-xs text-violet-400 hover:text-violet-300 font-medium">Manage</button>
                      </div>

                      <div className="space-y-4 flex-1 overflow-y-auto max-h-96 pr-1">
                        <div>
                          <h4 className="text-xs font-semibold uppercase tracking-wider text-zinc-500 mb-2.5">Images Queue ({imagesQueue.length})</h4>
                          {imagesQueue.length === 0 ? (
                            <div className="text-zinc-600 text-xs font-mono py-2 italic">No pending images in queue.</div>
                          ) : (
                            <div className="space-y-2">
                              {imagesQueue.slice(0, 3).map((item) => (
                                <div key={item.id} className="p-3 bg-zinc-900/50 border border-zinc-800/80 rounded-xl flex items-center justify-between gap-3">
                                  <span className="text-xs text-zinc-300 truncate font-mono">{item.prompt}</span>
                                  <span className="px-2 py-0.5 rounded bg-yellow-500/10 text-yellow-400 text-[9px] font-semibold shrink-0 uppercase tracking-widest">Pending</span>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>

                        <div className="border-t border-zinc-900 pt-4">
                          <h4 className="text-xs font-semibold uppercase tracking-wider text-zinc-500 mb-2.5">Videos Queue ({videosQueue.length})</h4>
                          {videosQueue.length === 0 ? (
                            <div className="text-zinc-600 text-xs font-mono py-2 italic">No pending videos in queue.</div>
                          ) : (
                            <div className="space-y-2">
                              {videosQueue.slice(0, 3).map((item) => (
                                <div key={item.id} className="p-3 bg-zinc-900/50 border border-zinc-800/80 rounded-xl flex items-center justify-between gap-3">
                                  <span className="text-xs text-zinc-300 truncate font-mono">{item.prompt}</span>
                                  <span className="px-2 py-0.5 rounded bg-yellow-500/10 text-yellow-400 text-[9px] font-semibold shrink-0 uppercase tracking-widest">Pending</span>
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
                  <div className="flex flex-col sm:flex-row gap-4 items-center justify-between bg-zinc-950/40 p-4 border border-zinc-900 rounded-2xl">
                    <div className="flex gap-2">
                      <button
                        onClick={() => setMediaFilter('all')}
                        className={`px-4 py-2 text-xs font-bold rounded-xl transition-all ${mediaFilter === 'all' ? 'bg-violet-600 text-white' : 'bg-zinc-900 text-zinc-400 hover:text-white'
                          }`}
                      >
                        All Assets ({mediaAssets.length})
                      </button>
                      <button
                        onClick={() => setMediaFilter('image')}
                        className={`px-4 py-2 text-xs font-bold rounded-xl transition-all ${mediaFilter === 'image' ? 'bg-violet-600 text-white' : 'bg-zinc-900 text-zinc-400 hover:text-white'
                          }`}
                      >
                        Images ({mediaAssets.filter(a => a.type === 'image').length})
                      </button>
                      <button
                        onClick={() => setMediaFilter('video')}
                        className={`px-4 py-2 text-xs font-bold rounded-xl transition-all ${mediaFilter === 'video' ? 'bg-violet-600 text-white' : 'bg-zinc-900 text-zinc-400 hover:text-white'
                          }`}
                      >
                        Videos ({mediaAssets.filter(a => a.type === 'video').length})
                      </button>
                    </div>

                    <div className="text-zinc-500 text-xs font-mono">
                      Showing {filteredMedia.length} of {mediaAssets.length} total generated entries
                    </div>
                  </div>

                  {/* Grid outputs */}
                  {filteredMedia.length === 0 ? (
                    <div className="text-center py-24 backdrop-blur-md bg-zinc-950/20 border border-zinc-900 rounded-2xl text-zinc-500">
                      No media files matched the active filters.
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      {filteredMedia.map((asset) => {
                        const uniqueKey = `${asset.type}-${asset.id}`;
                        const isPreviewing = !!activePreviews[uniqueKey];
                        const previewUrl = activePreviews[uniqueKey];

                        return (
                          <div
                            key={uniqueKey}
                            className="backdrop-blur-md bg-zinc-950/45 border border-zinc-900 rounded-2xl overflow-hidden hover:border-violet-500/35 hover:shadow-[0_4px_30px_rgba(139,92,246,0.1)] transition-all duration-300 flex flex-col h-full"
                          >
                            {/* Media content body */}
                            <div className="aspect-video w-full bg-zinc-900 border-b border-zinc-900 flex items-center justify-center relative group">
                              {isPreviewing && previewUrl ? (
                                asset.type === 'image' ? (
                                  // eslint-disable-next-line @next/next/no-img-element
                                  <img src={previewUrl} alt={asset.alt_text} className="w-full h-full object-contain" />
                                ) : (
                                  <video src={previewUrl} controls autoPlay className="w-full h-full object-contain" />
                                )
                              ) : (
                                <div className="flex flex-col items-center justify-center text-center p-4">
                                  <div className="w-14 h-14 rounded-full bg-zinc-950 flex items-center justify-center border border-zinc-800 text-zinc-500 mb-3 group-hover:text-violet-400 group-hover:border-violet-500/20 transition-all">
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
                                  <span className="text-zinc-600 text-[10px] font-mono tracking-wider block mb-2">{asset.filename}</span>
                                  <button
                                    onClick={() => handlePreviewMedia(asset, uniqueKey)}
                                    className="px-4 py-2 bg-violet-600 text-white rounded-xl text-xs font-bold shadow-lg shadow-violet-600/30 hover:bg-violet-500 hover:scale-[1.02] active:scale-[0.98] transition-all"
                                  >
                                    {signingUrlId === uniqueKey ? 'Signing...' : `Reveal ${asset.type.toUpperCase()}`}
                                  </button>
                                </div>
                              )}

                              {isPreviewing && (
                                <button
                                  onClick={() => handlePreviewMedia(asset, uniqueKey)}
                                  className="absolute top-3 right-3 bg-zinc-950/80 hover:bg-zinc-950 p-2 rounded-lg text-zinc-400 hover:text-white border border-zinc-800 transition-all z-10"
                                >
                                  Close Preview
                                </button>
                              )}
                            </div>

                            {/* Details body */}
                            <div className="p-5 flex-1 flex flex-col justify-between space-y-4">
                              <div className="space-y-2">
                                <span className="px-2.5 py-0.5 rounded-full bg-zinc-900 border border-zinc-800 text-zinc-400 text-[9px] font-mono uppercase tracking-wider inline-block">
                                  {asset.model || 'Unknown Model'}
                                </span>
                                <h3 className="font-bold text-white text-sm line-clamp-2" title={asset.prompt}>
                                  {asset.prompt}
                                </h3>
                                {asset.description && (
                                  <p className="text-xs text-zinc-400 line-clamp-3 leading-relaxed">
                                    {asset.description}
                                  </p>
                                )}
                              </div>

                              <div className="pt-3 border-t border-zinc-900 flex items-center justify-between text-[11px] text-zinc-500">
                                <span>{new Date(asset.created_at).toLocaleDateString()}</span>
                                <div className="flex items-center gap-1.5">
                                  {asset.posted_insta ? (
                                    <span className="px-2 py-0.5 rounded bg-fuchsia-950/45 border border-fuchsia-900/40 text-fuchsia-400 font-medium">Insta Shared</span>
                                  ) : (
                                    <span className="px-2 py-0.5 rounded bg-zinc-900 text-zinc-600">Insta Off</span>
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
                                      <span className="px-2 py-0.5 rounded bg-zinc-900 text-zinc-600">YT Off</span>
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
                    <div className="backdrop-blur-md bg-zinc-950/40 border border-zinc-900 rounded-2xl p-6">
                      <h3 className="font-bold text-white text-base mb-5">Queue New Generation</h3>

                      <form onSubmit={handleAddPrompt} className="space-y-5">
                        <div>
                          <label className="block text-xs font-semibold uppercase tracking-wider text-zinc-400 mb-2">Asset Type</label>
                          <div className="grid grid-cols-2 gap-2">
                            <button
                              type="button"
                              onClick={() => setNewType('image')}
                              className={`py-2 px-4 rounded-xl text-xs font-bold border transition-all ${newType === 'image'
                                  ? 'bg-violet-600 text-white border-violet-500'
                                  : 'bg-zinc-900 text-zinc-400 border-zinc-800 hover:text-white'
                                }`}
                            >
                              Image Prompt
                            </button>
                            <button
                              type="button"
                              onClick={() => setNewType('video')}
                              className={`py-2 px-4 rounded-xl text-xs font-bold border transition-all ${newType === 'video'
                                  ? 'bg-violet-600 text-white border-violet-500'
                                  : 'bg-zinc-900 text-zinc-400 border-zinc-800 hover:text-white'
                                }`}
                            >
                              Video Script
                            </button>
                          </div>
                        </div>

                        <div>
                          <label htmlFor="promptInput" className="block text-xs font-semibold uppercase tracking-wider text-zinc-400 mb-2">Prompt / Deity Name</label>
                          <textarea
                            id="promptInput"
                            rows={3}
                            placeholder="e.g. Shiva, Hanuman, or custom scene details..."
                            value={newPrompt}
                            onChange={(e) => setNewPrompt(e.target.value)}
                            className="w-full px-4 py-3 bg-zinc-900/50 border border-zinc-800 rounded-xl text-white placeholder-zinc-600 focus:outline-none focus:border-violet-500/80 transition-all font-mono text-xs"
                            required
                          />
                        </div>

                        <div className="space-y-3 bg-zinc-900/20 border border-zinc-900/50 p-4 rounded-xl">
                          <span className="block text-xs font-semibold uppercase tracking-wider text-zinc-500 mb-1">Post Automation</span>

                          <label className="flex items-center gap-3 cursor-pointer select-none">
                            <input
                              type="checkbox"
                              checked={autoInsta}
                              onChange={(e) => setAutoInsta(e.target.checked)}
                              className="accent-violet-600 rounded"
                            />
                            <span className="text-xs text-zinc-300">Instagram Feed / Reels publish</span>
                          </label>

                          <label className="flex items-center gap-3 cursor-pointer select-none">
                            <input
                              type="checkbox"
                              checked={autoYt}
                              onChange={(e) => setAutoYt(e.target.checked)}
                              className="accent-violet-600 rounded"
                            />
                            <span className="text-xs text-zinc-300">YouTube Shorts publish (video only)</span>
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
                          className="w-full py-3 bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-500 hover:to-fuchsia-500 text-white rounded-xl text-xs font-bold transition-all shadow-[0_4px_15px_rgba(139,92,246,0.3)] disabled:opacity-50"
                        >
                          {submittingPrompt ? 'Adding...' : 'Enqueue Generation'}
                        </button>
                      </form>
                    </div>

                    {/* Active Queue lists */}
                    <div className="lg:col-span-2 backdrop-blur-md bg-zinc-950/40 border border-zinc-900 rounded-2xl p-6">
                      <h3 className="font-bold text-white text-base mb-5">Pending Pipeline Items</h3>

                      <div className="space-y-6">
                        {/* Images */}
                        <div>
                          <div className="flex items-center justify-between mb-3">
                            <h4 className="text-xs font-bold uppercase tracking-wider text-zinc-400">Images Generator Queue ({imagesQueue.length})</h4>
                            <span className="text-[10px] text-zinc-600 font-mono">TABLE: images_on_demand</span>
                          </div>

                          {imagesQueue.length === 0 ? (
                            <div className="text-center py-6 border border-dashed border-zinc-900 rounded-xl text-zinc-600 text-xs italic">
                              Queue empty. Use generator form to create entries.
                            </div>
                          ) : (
                            <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                              {imagesQueue.map((item) => (
                                <div key={item.id} className="p-3 bg-zinc-900/30 border border-zinc-900 rounded-xl flex items-center justify-between gap-3 hover:border-zinc-800 transition-all">
                                  <div className="truncate">
                                    <span className="text-xs text-zinc-300 font-mono block truncate">{item.prompt}</span>
                                    <span className="text-[9px] text-zinc-500 block mt-1">
                                      Enqueued: {new Date(item.created_at).toLocaleString()}
                                    </span>
                                  </div>
                                  <div className="flex items-center gap-3 shrink-0">
                                    <span className="px-2 py-0.5 rounded bg-yellow-500/10 text-yellow-500 text-[9px] uppercase tracking-wider">Queue</span>
                                    <button
                                      onClick={() => handleDeleteQueueItem('image', item.id)}
                                      className="p-1 rounded bg-zinc-950 hover:bg-red-950 border border-zinc-850 hover:border-red-900 text-zinc-500 hover:text-red-400 transition-all"
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
                        <div className="border-t border-zinc-900 pt-4">
                          <div className="flex items-center justify-between mb-3">
                            <h4 className="text-xs font-bold uppercase tracking-wider text-zinc-400">Videos Generator Queue ({videosQueue.length})</h4>
                            <span className="text-[10px] text-zinc-600 font-mono">TABLE: videos_on_demand</span>
                          </div>

                          {videosQueue.length === 0 ? (
                            <div className="text-center py-6 border border-dashed border-zinc-900 rounded-xl text-zinc-600 text-xs italic">
                              Queue empty. Use generator form to create entries.
                            </div>
                          ) : (
                            <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                              {videosQueue.map((item) => (
                                <div key={item.id} className="p-3 bg-zinc-900/30 border border-zinc-900 rounded-xl flex items-center justify-between gap-3 hover:border-zinc-800 transition-all">
                                  <div className="truncate">
                                    <span className="text-xs text-zinc-300 font-mono block truncate">{item.prompt}</span>
                                    <span className="text-[9px] text-zinc-500 block mt-1">
                                      Enqueued: {new Date(item.created_at).toLocaleString()}
                                    </span>
                                  </div>
                                  <div className="flex items-center gap-3 shrink-0">
                                    <span className="px-2 py-0.5 rounded bg-yellow-500/10 text-yellow-500 text-[9px] uppercase tracking-wider">Queue</span>
                                    <button
                                      onClick={() => handleDeleteQueueItem('video', item.id)}
                                      className="p-1 rounded bg-zinc-950 hover:bg-red-950 border border-zinc-850 hover:border-red-900 text-zinc-500 hover:text-red-400 transition-all"
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
                  <div className="backdrop-blur-md bg-zinc-950/40 border border-zinc-900 rounded-2xl overflow-hidden">
                    <div className="px-6 py-5 border-b border-zinc-900 flex flex-col sm:flex-row gap-4 items-center justify-between">
                      <div>
                        <h3 className="font-bold text-white text-base">Google Cloud Storage bucket explorer</h3>
                        <p className="text-xs text-zinc-500 mt-1 font-mono">Bucket: databucket_reels_photos</p>
                      </div>

                      <div className="text-zinc-400 text-xs font-mono">
                        Objects listed: {gcsFiles.length} files
                      </div>
                    </div>

                    {gcsFiles.length === 0 ? (
                      <div className="text-center py-20 text-zinc-500 text-sm font-mono">No files found inside the GCS bucket.</div>
                    ) : (
                      <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                          <thead>
                            <tr className="border-b border-zinc-900 text-zinc-400 text-xs font-semibold uppercase font-mono tracking-wider bg-zinc-950/30">
                              <th className="py-4 px-6">Name</th>
                              <th className="py-4 px-6">Content Type</th>
                              <th className="py-4 px-6">Size</th>
                              <th className="py-4 px-6">Updated At</th>
                              <th className="py-4 px-6 text-right">Preview Actions</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-zinc-900 text-sm">
                            {gcsFiles.map((file) => {
                              const uniqueKey = `gcs-${file.name}`;
                              const isPreviewing = !!activePreviews[uniqueKey];
                              const previewUrl = activePreviews[uniqueKey];

                              return (
                                <React.Fragment key={file.id || file.name}>
                                  <tr className="hover:bg-zinc-900/20 transition-all">
                                    <td className="py-4 px-6 font-mono text-xs text-zinc-300 max-w-xs truncate" title={file.name}>
                                      {file.name}
                                    </td>
                                    <td className="py-4 px-6 font-mono text-xs text-zinc-500">
                                      {file.contentType}
                                    </td>
                                    <td className="py-4 px-6 text-zinc-400 font-mono text-xs">
                                      {formatBytes(file.size)}
                                    </td>
                                    <td className="py-4 px-6 text-zinc-500 text-xs">
                                      {new Date(file.updated).toLocaleString()}
                                    </td>
                                    <td className="py-4 px-6 text-right">
                                      <div className="flex items-center justify-end gap-2">
                                        <button
                                          onClick={() => handlePreviewMedia(file.name, uniqueKey)}
                                          className="px-3 py-1.5 bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 rounded-lg text-xs font-semibold text-zinc-300 hover:text-white transition-all"
                                        >
                                          {signingUrlId === uniqueKey ? 'Signing...' : isPreviewing ? 'Hide' : 'Reveal Link'}
                                        </button>

                                        {isPreviewing && previewUrl && (
                                          <a
                                            href={previewUrl}
                                            target="_blank"
                                            rel="noreferrer"
                                            className="px-3 py-1.5 bg-violet-600 hover:bg-violet-500 rounded-lg text-xs font-semibold text-white transition-all inline-flex items-center gap-1"
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
                                    <tr className="bg-zinc-950/40">
                                      <td colSpan={5} className="py-4 px-6 border-b border-zinc-900">
                                        <div className="max-w-xl mx-auto rounded-xl overflow-hidden border border-zinc-850 shadow-inner bg-zinc-950 flex items-center justify-center p-3 relative">
                                          {file.contentType.startsWith('image/') ? (
                                            // eslint-disable-next-line @next/next/no-img-element
                                            <img src={previewUrl} alt={file.name} className="max-h-64 object-contain rounded" />
                                          ) : file.contentType.startsWith('video/') ? (
                                            <video src={previewUrl} controls className="max-h-64 object-contain rounded w-full" />
                                          ) : (
                                            <div className="p-8 text-center text-zinc-500 font-mono text-xs">
                                              No preview available for content type: {file.contentType}
                                              <div className="mt-3">
                                                <a href={previewUrl} download className="text-violet-400 hover:underline">Download file directly</a>
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
                    <div className="p-4 bg-zinc-900/40 border border-zinc-800 rounded-xl">
                      <span className="text-zinc-500 text-[10px] font-semibold uppercase tracking-wider block">Total Impressions</span>
                      <span className="text-xl font-bold text-white mt-1 block">{analytics.sums.impressions.toLocaleString()}</span>
                    </div>
                    <div className="p-4 bg-zinc-900/40 border border-zinc-800 rounded-xl">
                      <span className="text-zinc-500 text-[10px] font-semibold uppercase tracking-wider block">Reach Reach</span>
                      <span className="text-xl font-bold text-white mt-1 block">{analytics.sums.reach.toLocaleString()}</span>
                    </div>
                    <div className="p-4 bg-zinc-900/40 border border-zinc-800 rounded-xl">
                      <span className="text-zinc-500 text-[10px] font-semibold uppercase tracking-wider block">Total Likes</span>
                      <span className="text-xl font-bold text-white mt-1 block">{analytics.sums.likes.toLocaleString()}</span>
                    </div>
                    <div className="p-4 bg-zinc-900/40 border border-zinc-800 rounded-xl">
                      <span className="text-zinc-500 text-[10px] font-semibold uppercase tracking-wider block">Total Comments</span>
                      <span className="text-xl font-bold text-white mt-1 block">{analytics.sums.comments.toLocaleString()}</span>
                    </div>
                    <div className="p-4 bg-zinc-900/40 border border-zinc-800 rounded-xl">
                      <span className="text-zinc-500 text-[10px] font-semibold uppercase tracking-wider block">Total Shares</span>
                      <span className="text-xl font-bold text-white mt-1 block">{analytics.sums.shares.toLocaleString()}</span>
                    </div>
                    <div className="p-4 bg-zinc-900/40 border border-zinc-800 rounded-xl">
                      <span className="text-zinc-500 text-[10px] font-semibold uppercase tracking-wider block">Total Saves</span>
                      <span className="text-xl font-bold text-white mt-1 block">{analytics.sums.saves.toLocaleString()}</span>
                    </div>
                  </div>

                  {/* SVG Interactions Chart */}
                  <div className="backdrop-blur-md bg-zinc-950/40 border border-zinc-900 rounded-2xl p-6">
                    <h3 className="font-bold text-white text-base mb-6">Interaction Analytics Visualization</h3>

                    {/* Dynamic custom SVG bar chart */}
                    <div className="w-full aspect-[21/9] bg-zinc-950/40 rounded-xl p-4 border border-zinc-900 flex flex-col justify-between">
                      {/* SVG Canvas */}
                      <div className="w-full flex-1 flex items-end gap-6 relative pt-6 px-4">
                        {/* Grid lines */}
                        <div className="absolute inset-x-0 bottom-0 top-6 border-b border-zinc-900 flex flex-col justify-between pointer-events-none">
                          <div className="w-full border-t border-zinc-900/20" />
                          <div className="w-full border-t border-zinc-900/25" />
                          <div className="w-full border-t border-zinc-900/35" />
                          <div className="w-full border-t border-zinc-900/50" />
                        </div>

                        {/* Impressions Bar */}
                        <div className="flex-1 flex flex-col items-center justify-end h-full gap-2 relative z-10 group">
                          <div className="w-full max-w-[80px] bg-gradient-to-t from-violet-600/80 to-violet-500 rounded-t-lg transition-all duration-500 hover:opacity-90 shadow-[0_0_15px_rgba(139,92,246,0.3)]" style={{ height: '70%' }}>
                            <div className="absolute -top-6 left-1/2 -translate-x-1/2 bg-zinc-900 px-2 py-0.5 rounded border border-zinc-800 text-[10px] text-zinc-300 opacity-0 group-hover:opacity-100 transition-all font-mono pointer-events-none">
                              {analytics.sums.impressions}
                            </div>
                          </div>
                          <span className="text-[10px] text-zinc-500 font-mono">Impressions</span>
                        </div>

                        {/* Reach Bar */}
                        <div className="flex-1 flex flex-col items-center justify-end h-full gap-2 relative z-10 group">
                          <div className="w-full max-w-[80px] bg-gradient-to-t from-cyan-600/80 to-cyan-500 rounded-t-lg transition-all duration-500 hover:opacity-90 shadow-[0_0_15px_rgba(6,182,212,0.3)]" style={{ height: '55%' }}>
                            <div className="absolute -top-6 left-1/2 -translate-x-1/2 bg-zinc-900 px-2 py-0.5 rounded border border-zinc-800 text-[10px] text-zinc-300 opacity-0 group-hover:opacity-100 transition-all font-mono pointer-events-none">
                              {analytics.sums.reach}
                            </div>
                          </div>
                          <span className="text-[10px] text-zinc-500 font-mono">Reach</span>
                        </div>

                        {/* Likes Bar */}
                        <div className="flex-1 flex flex-col items-center justify-end h-full gap-2 relative z-10 group">
                          <div className="w-full max-w-[80px] bg-gradient-to-t from-rose-600/80 to-rose-500 rounded-t-lg transition-all duration-500 hover:opacity-90 shadow-[0_0_15px_rgba(244,63,94,0.3)]" style={{ height: '40%' }}>
                            <div className="absolute -top-6 left-1/2 -translate-x-1/2 bg-zinc-900 px-2 py-0.5 rounded border border-zinc-800 text-[10px] text-zinc-300 opacity-0 group-hover:opacity-100 transition-all font-mono pointer-events-none">
                              {analytics.sums.likes}
                            </div>
                          </div>
                          <span className="text-[10px] text-zinc-500 font-mono">Likes</span>
                        </div>

                        {/* Comments Bar */}
                        <div className="flex-1 flex flex-col items-center justify-end h-full gap-2 relative z-10 group">
                          <div className="w-full max-w-[80px] bg-gradient-to-t from-amber-600/80 to-amber-500 rounded-t-lg transition-all duration-500 hover:opacity-90 shadow-[0_0_15px_rgba(245,158,11,0.3)]" style={{ height: '25%' }}>
                            <div className="absolute -top-6 left-1/2 -translate-x-1/2 bg-zinc-900 px-2 py-0.5 rounded border border-zinc-800 text-[10px] text-zinc-300 opacity-0 group-hover:opacity-100 transition-all font-mono pointer-events-none">
                              {analytics.sums.comments}
                            </div>
                          </div>
                          <span className="text-[10px] text-zinc-500 font-mono">Comments</span>
                        </div>

                        {/* Shares Bar */}
                        <div className="flex-1 flex flex-col items-center justify-end h-full gap-2 relative z-10 group">
                          <div className="w-full max-w-[80px] bg-gradient-to-t from-fuchsia-600/80 to-fuchsia-500 rounded-t-lg transition-all duration-500 hover:opacity-90 shadow-[0_0_15px_rgba(217,70,239,0.3)]" style={{ height: '18%' }}>
                            <div className="absolute -top-6 left-1/2 -translate-x-1/2 bg-zinc-900 px-2 py-0.5 rounded border border-zinc-800 text-[10px] text-zinc-300 opacity-0 group-hover:opacity-100 transition-all font-mono pointer-events-none">
                              {analytics.sums.shares}
                            </div>
                          </div>
                          <span className="text-[10px] text-zinc-500 font-mono">Shares</span>
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
