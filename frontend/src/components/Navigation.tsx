import { useState, useEffect } from 'react';
import { Music, Database, Settings } from 'lucide-react';

export default function Navigation() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    function onScroll() {
      setScrolled(window.scrollY > 80);
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const scrollTo = (id: string) => {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <nav
      className={`fixed top-0 left-0 w-full z-50 transition-all duration-500 ${
        scrolled
          ? 'bg-[#050505]/80 backdrop-blur-xl border-b border-white/5'
          : 'bg-transparent'
      }`}
    >
      <div className="max-w-[1400px] mx-auto px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-full bg-[#e1f739]/20 flex items-center justify-center">
            <Music className="w-3.5 h-3.5 text-[#e1f739]" />
          </div>
          <span
            className="text-white font-semibold text-sm tracking-wide"
            style={{ fontFamily: "-apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif" }}
          >
            觅知音
          </span>
          <span className="font-mono-data text-[10px] text-white/30 ml-1">
            MZSS v1.0
          </span>
        </div>

        <div className="hidden md:flex items-center gap-8">
          <button
            onClick={() => scrollTo('hero')}
            className="font-mono-data text-[11px] text-white/40 hover:text-[#e1f739] transition-colors duration-300"
          >
            SPATIAL ENGINE
          </button>
          <button
            onClick={() => scrollTo('features')}
            className="font-mono-data text-[11px] text-white/40 hover:text-[#e1f739] transition-colors duration-300"
          >
            FEATURE ANALYSIS
          </button>
          <button
            onClick={() => scrollTo('gallery')}
            className="font-mono-data text-[11px] text-white/40 hover:text-[#e1f739] transition-colors duration-300"
          >
            MUSIC ARCHIVE
          </button>
        </div>

        <div className="flex items-center gap-4">
          <Database className="w-4 h-4 text-white/20 hover:text-[#e1f739] transition-colors cursor-pointer" />
          <Settings className="w-4 h-4 text-white/20 hover:text-[#e1f739] transition-colors cursor-pointer" />
        </div>
      </div>
    </nav>
  );
}
