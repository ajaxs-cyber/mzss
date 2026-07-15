import { useRef, useEffect } from 'react';
import { tracks } from '@/data/musicLibrary';
import { Play, Heart, BarChart3 } from 'lucide-react';

function TrackCard({ track, index }: { track: (typeof tracks)[0]; index: number }) {
  const cardRef = useRef<HTMLDivElement>(null);

  return (
    <div
      ref={cardRef}
      className="gallery-item group relative rounded-2xl overflow-hidden cursor-pointer"
      style={{
        animationDelay: `${index * 80}ms`,
      }}
    >
      {/* Image */}
      <div className="aspect-square overflow-hidden">
        <img
          src={track.cover}
          alt={track.title}
          className="gallery-item-img w-full h-full object-cover"
          loading="lazy"
        />
      </div>

      {/* Overlay Info */}
      <div className="absolute inset-x-0 bottom-0 translate-y-full group-hover:translate-y-0 transition-transform duration-500 ease-[cubic-bezier(0.16,1,0.3,1)]">
        <div className="p-5 bg-gradient-to-t from-[#050505]/95 via-[#050505]/80 to-transparent">
          <div className="flex items-start justify-between mb-2">
            <div>
              <h3 className="text-white text-sm font-medium mb-0.5">{track.title}</h3>
              <p className="font-mono-data text-[10px] text-white/40">
                {track.artist}
              </p>
            </div>
            <button className="w-8 h-8 rounded-full bg-[#e1f739]/90 flex items-center justify-center hover:bg-[#e1f739] transition-colors flex-shrink-0">
              <Play className="w-3.5 h-3.5 text-[#050505] ml-0.5" />
            </button>
          </div>

          <div className="flex flex-wrap gap-1.5 mb-3">
            {track.tags.map((tag) => (
              <span
                key={tag}
                className="font-mono-data text-[9px] px-2 py-0.5 rounded-full bg-white/5 text-white/40"
              >
                {tag}
              </span>
            ))}
          </div>

          <div className="flex items-center justify-between text-[11px]" style={{ color: 'rgba(255, 255, 255, 0.5)' }}>
            <span>{track.genre}</span>
            <span className="font-mono-data">{track.bpm} BPM</span>
            <span>{track.duration}</span>
          </div>

          {/* Mini emotion bars */}
          <div className="mt-3 flex gap-1">
            {[
              { label: '效价', value: track.valence },
              { label: '唤醒', value: track.arousal },
              { label: '温暖', value: track.warmth },
              { label: '紧张', value: track.tension },
            ].map((item) => (
              <div key={item.label} className="flex-1">
                <div className="font-mono-data text-[8px] text-white/25 mb-0.5 text-center">
                  {item.label}
                </div>
                <div className="h-1 bg-white/5 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-[#e1f739]/70 rounded-full"
                    style={{ width: `${(item.value / 7) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Scene Badge */}
      <div className="absolute top-3 left-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
        <span className="font-mono-data text-[9px] px-2.5 py-1 rounded-full bg-black/50 backdrop-blur-sm text-white/60">
          {track.sceneType}
        </span>
      </div>

      {/* Top Right Actions */}
      <div className="absolute top-3 right-3 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
        <button className="w-7 h-7 rounded-full bg-black/40 backdrop-blur-sm flex items-center justify-center hover:bg-[#e1f739]/20 transition-colors">
          <Heart className="w-3 h-3 text-white/60" />
        </button>
        <button className="w-7 h-7 rounded-full bg-black/40 backdrop-blur-sm flex items-center justify-center hover:bg-[#e1f739]/20 transition-colors">
          <BarChart3 className="w-3 h-3 text-white/60" />
        </button>
      </div>
    </div>
  );
}

export default function GallerySection() {
  const sectionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const section = sectionRef.current;
    if (!section) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            section.classList.add('in-view');
          }
        });
      },
      { threshold: 0.1 }
    );

    observer.observe(section);
    return () => observer.disconnect();
  }, []);

  return (
    <section
      id="gallery"
      ref={sectionRef}
      className="relative py-40"
      style={{ zIndex: 2 }}
    >
      <div className="max-w-[1400px] mx-auto px-8">
        {/* Section Header */}
        <div className="mb-16 flex items-end justify-between">
          <div>
            <span className="font-mono-data text-[11px] text-[#e1f739] tracking-wider">
              MUSIC ARCHIVE
            </span>
            <h2
              className="text-white font-semibold mt-3 tracking-[-0.02em]"
              style={{ fontSize: 'clamp(32px, 4vw, 48px)' }}
            >
              资产档案库
            </h2>
            <p
              className="mt-4 text-[15px] leading-[1.8] max-w-[480px]"
              style={{ color: 'rgba(255, 255, 255, 0.7)' }}
            >
              涵盖深夜电台、精品酒店、沉浸式展览等多场景的背景音乐素材，
              每首曲目均经过特征提取与情绪量化标注
            </p>
          </div>

          <div className="hidden md:flex items-center gap-2">
            <span className="font-mono-data text-[10px] text-white/30">
              {tracks.length} TRACKS
            </span>
            <div className="w-8 h-px bg-white/10" />
          </div>
        </div>

        {/* Gallery Grid */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {tracks.map((track, index) => (
            <TrackCard key={track.id} track={track} index={index} />
          ))}
        </div>

        {/* Bottom Stats */}
        <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-6">
          {[
            { label: 'TOTAL TRACKS', value: '24', unit: '首' },
            { label: 'GENRES', value: '8', unit: '种风格' },
            { label: 'SCENE TEMPLATES', value: '4', unit: '类场景' },
            { label: 'EMOTION DIMS', value: '7', unit: '维指标' },
          ].map((stat) => (
            <div
              key={stat.label}
              className="text-center py-6 rounded-xl bg-white/[0.02] border border-white/5"
            >
              <div className="text-[#e1f739] text-2xl font-semibold mb-1">
                {stat.value}
              </div>
              <div className="font-mono-data text-[10px] text-white/30 mb-1">
                {stat.label}
              </div>
              <div className="text-[12px]" style={{ color: 'rgba(255, 255, 255, 0.4)' }}>
                {stat.unit}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
