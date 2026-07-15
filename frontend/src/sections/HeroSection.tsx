import LiquidGlass from '@/components/LiquidGlass';
import Waveform from '@/components/Waveform';

export default function HeroSection() {
  return (
    <section
      id="hero"
      className="relative min-h-screen flex items-center justify-center overflow-hidden"
      style={{ zIndex: 1 }}
    >
      {/* Central Title */}
      <div className="absolute left-[8%] top-1/2 -translate-y-1/2 max-w-[600px]">
        <h1
          className="text-white font-semibold leading-[1.05] tracking-[-0.02em] mb-5"
          style={{ fontSize: 'clamp(40px, 5vw, 64px)' }}
        >
          空间情绪引擎
        </h1>
        <p className="font-mono-data text-[11px] text-white/40 tracking-[0.15em]">
          SONIC ARCHITECTURE FOR SPATIAL BRANDING
        </p>
        <p
          className="mt-6 text-[15px] leading-[1.8] max-w-[440px]"
          style={{ color: 'rgba(255, 255, 255, 0.7)' }}
        >
          将音乐的可测量属性与客户场景的目标情绪进行量化匹配，
          为品牌页面、公益项目与线下空间提供可解释的背景音乐推荐框架。
        </p>
        <div className="flex gap-4 mt-8">
          <button
            onClick={() => document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })}
            className="px-6 py-2.5 rounded-full bg-[#e1f739] text-[#050505] text-xs font-semibold hover:bg-[#d4ea35] transition-colors"
          >
            探索特征分析
          </button>
          <button
            onClick={() => document.getElementById('gallery')?.scrollIntoView({ behavior: 'smooth' })}
            className="px-6 py-2.5 rounded-full border border-white/15 text-white/70 text-xs hover:border-white/30 hover:text-white transition-colors"
          >
            浏览音乐库
          </button>
        </div>
      </div>

      {/* Liquid Glass Control Panel - Bottom Right */}
      <div className="absolute right-[5%] bottom-[12%] w-[320px]">
        <LiquidGlass strong>
          <div className="p-6">
            <div className="flex items-center justify-between mb-4">
              <span className="font-mono-data text-[10px] text-white/40">
                REAL-TIME METRICS
              </span>
              <div className="flex items-center gap-1.5">
                <div className="w-1.5 h-1.5 rounded-full bg-[#e1f739] animate-pulse" />
                <span className="font-mono-data text-[10px] text-[#e1f739]">
                  LIVE
                </span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-5">
              <div>
                <div className="font-mono-data text-[10px] text-white/30 mb-1">
                  BPM RANGE
                </div>
                <div className="text-white text-sm font-medium">
                  68 — 118
                </div>
              </div>
              <div>
                <div className="font-mono-data text-[10px] text-white/30 mb-1">
                  KEY SIGNATURE
                </div>
                <div className="text-white text-sm font-medium">
                  Cmaj / Amin
                </div>
              </div>
              <div>
                <div className="font-mono-data text-[10px] text-white/30 mb-1">
                  LUFS
                </div>
                <div className="text-white text-sm font-medium">
                  -14 to -24
                </div>
              </div>
              <div>
                <div className="font-mono-data text-[10px] text-white/30 mb-1">
                  TRACKS
                </div>
                <div className="text-[#e1f739] text-sm font-medium">24</div>
              </div>
            </div>

            <Waveform />
          </div>
        </LiquidGlass>
      </div>

      {/* Scroll Indicator */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2">
        <span className="font-mono-data text-[10px] text-white/20">SCROLL</span>
        <div className="w-px h-8 bg-gradient-to-b from-white/20 to-transparent" />
      </div>
    </section>
  );
}
