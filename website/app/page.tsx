import Link from 'next/link';

export default function Home() {
  return (
    <div className="relative min-h-screen w-full flex flex-col items-center justify-center bg-[#070913] text-zinc-100 overflow-hidden font-sans">
      {/* Gradient ambient glow */}
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] rounded-full bg-blue-600/10 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-1/4 left-1/4 w-[300px] h-[300px] rounded-full bg-cyan-600/5 blur-[100px] pointer-events-none" />

      {/* Cyberpunk grid background */}
      <div
        className="absolute inset-0 opacity-[0.02] pointer-events-none"
        style={{
          backgroundImage: `
            linear-gradient(to right, rgb(255,255,255) 1px, transparent 1px),
            linear-gradient(to bottom, rgb(255,255,255) 1px, transparent 1px)
          `,
          backgroundSize: '50px 50px',
        }}
      />

      <main className="relative z-10 text-center px-6 max-w-2xl space-y-8 flex flex-col items-center">
        {/* Glowing Platform Icon */}
        <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-blue-600 to-cyan-500 flex items-center justify-center shadow-[0_0_30px_rgba(37,99,235,0.45)] mb-2 select-none">
          <span className="text-white font-black text-2xl tracking-tighter">AG</span>
        </div>

        <div className="space-y-4">
          <span className="px-3 py-1 rounded-full bg-blue-950/30 border border-blue-900/40 text-blue-400 text-xs font-semibold tracking-wider uppercase font-mono">
            Platform Automation Engine
          </span>
          <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-white leading-tight">
            Automate Your Social Media Production
          </h1>
          <p className="text-zinc-400 text-sm sm:text-base max-w-lg mx-auto leading-relaxed">
            Generate stunning deity scenes and video docu-series using AI models, upload them to Cloud Storage, and auto-publish directly to Instagram and YouTube.
          </p>
        </div>

        <div className="flex justify-center gap-4 pt-4">
          <Link
            href="/dashboard"
            className="px-6 py-3.5 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-450 text-white font-semibold text-sm shadow-[0_4px_25px_rgba(37,99,235,0.35)] transition-all hover:scale-[1.03] active:scale-[0.97]"
          >
            Enter Console Dashboard
          </Link>
        </div>
      </main>

      <footer className="absolute bottom-6 font-mono text-[10px] text-zinc-700 select-none">
        Synaptic Flow Automated Posts Platform © {new Date().getFullYear()}
      </footer>
    </div>
  );
}
