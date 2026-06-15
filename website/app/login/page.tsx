'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const router = useRouter();
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!password) {
      setError('Please enter your administrator password.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ password }),
      });

      const data = await res.json();

      if (res.ok && data.success) {
        // Redirect to dashboard
        router.push('/dashboard');
        router.refresh();
      } else {
        setError(data.error || 'Invalid administrator password.');
      }
    } catch (err) {
      console.error('Login request failed:', err);
      setError('Connection failed. Please verify the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen w-full flex items-center justify-center bg-[#070913] overflow-hidden font-sans">
      {/* Decorative ambient glowing background circles */}
      <div className="absolute top-1/4 left-1/4 -translate-x-1/2 -translate-y-1/2 w-[350px] h-[350px] rounded-full bg-blue-600/10 blur-[80px]" />
      <div className="absolute bottom-1/4 right-1/4 translate-x-1/2 translate-y-1/2 w-[400px] h-[400px] rounded-full bg-cyan-500/10 blur-[100px]" />

      {/* Cyberpunk grid overlay */}
      <div 
        className="absolute inset-0 opacity-[0.03] pointer-events-none"
        style={{
          backgroundImage: `
            linear-gradient(to right, rgb(255,255,255) 1px, transparent 1px),
            linear-gradient(to bottom, rgb(255,255,255) 1px, transparent 1px)
          `,
          backgroundSize: '40px 40px',
        }}
      />

      <div className="relative z-10 w-full max-w-md px-6 py-12">
        {/* Main card */}
        <div className="backdrop-blur-xl bg-zinc-950/65 border border-zinc-800/80 rounded-2xl p-8 shadow-[0_0_50px_-12px_rgba(37,99,235,0.25)] hover:border-blue-500/35 transition-all duration-500">
          {/* Project Banner Header */}
          <div className="w-full h-24 rounded-xl overflow-hidden mb-6 border border-zinc-900 shadow-inner">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img 
              src="/project_banner.png" 
              alt=" Banner" 
              className="w-full h-full object-cover"
            />
          </div>

          <div className="flex flex-col items-center mb-8">
            {/* Glowing Logo */}
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-blue-600 to-cyan-500 flex items-center justify-center shadow-[0_0_20px_rgba(37,99,235,0.4)] mb-4 select-none">
              <span className="text-white font-black text-2xl tracking-tighter">AG</span>
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-white">Synaptic Flow Console</h1>
            <p className="text-zinc-400 text-sm mt-2 text-center">
              Enter your password to manage automated posts and cloud assets.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label 
                htmlFor="password" 
                className="block text-xs font-semibold uppercase tracking-wider text-zinc-400 mb-2"
              >
                Administrator Password
              </label>
              <input
                id="password"
                type="password"
                placeholder="••••••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 bg-zinc-900/50 border border-zinc-800 rounded-xl text-white placeholder-zinc-600 focus:outline-none focus:border-blue-500/80 focus:ring-1 focus:ring-blue-500/80 transition-all duration-300"
                disabled={loading}
              />
            </div>

            {error && (
              <div className="p-3.5 bg-red-950/40 border border-red-900/60 rounded-xl text-red-300 text-sm flex items-center gap-2 animate-shake">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5 flex-shrink-0 text-red-400">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z" />
                </svg>
                <span>{error}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="relative w-full py-3 px-4 rounded-xl font-medium text-white bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 active:scale-[0.98] transition-all duration-300 shadow-[0_4px_20px_rgba(37,99,235,0.3)] disabled:opacity-50 disabled:pointer-events-none overflow-hidden"
            >
              {loading ? (
                <div className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  <span>Authenticating...</span>
                </div>
              ) : (
                'Sign In'
              )}
            </button>
          </form>
        </div>

        {/* Footer info */}
        <p className="text-center text-xs text-zinc-600 mt-8 font-mono">
          Synaptic Flow Automated Posts Platform v1.0
        </p>
      </div>
    </div>
  );
}
