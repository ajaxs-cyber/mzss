import { useRef, useEffect } from 'react';
import LiquidGlass from '@/components/LiquidGlass';
import { emotionDimensions, sceneTemplates } from '@/data/musicLibrary';
import { Activity, Layers, Radio } from 'lucide-react';

function EmotionRadar() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const rafRef = useRef<number>(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d')!;
    const dpr = Math.min(window.devicePixelRatio, 2);
    const w = 400;
    const h = 400;
    canvas.width = w * dpr;
    canvas.height = h * dpr;
    ctx.scale(dpr, dpr);

    const values = [5.8, 4.2, 5.5, 2.5, 5.2, 4.8, 2.8];
    const labels = ['效价', '唤醒', '温暖', '紧张', '希望', '行动', '干扰'];
    const centerX = w / 2;
    const centerY = h / 2;
    const radius = 140;
    const n = values.length;

    let t = 0;
    function draw() {
      ctx!.clearRect(0, 0, w, h);

      // Grid circles
      for (let ring = 1; ring <= 4; ring++) {
        ctx!.beginPath();
        ctx!.strokeStyle = `rgba(255, 255, 255, ${0.03 + ring * 0.01})`;
        ctx!.lineWidth = 0.5;
        for (let i = 0; i <= n; i++) {
          const angle = (i * 2 * Math.PI) / n - Math.PI / 2;
          const r = (radius / 4) * ring;
          const x = centerX + Math.cos(angle) * r;
          const y = centerY + Math.sin(angle) * r;
          if (i === 0) ctx!.moveTo(x, y);
          else ctx!.lineTo(x, y);
        }
        ctx!.stroke();
      }

      // Axis lines
      for (let i = 0; i < n; i++) {
        const angle = (i * 2 * Math.PI) / n - Math.PI / 2;
        ctx!.beginPath();
        ctx!.strokeStyle = 'rgba(255, 255, 255, 0.05)';
        ctx!.lineWidth = 0.5;
        ctx!.moveTo(centerX, centerY);
        ctx!.lineTo(centerX + Math.cos(angle) * radius, centerY + Math.sin(angle) * radius);
        ctx!.stroke();

        // Labels
        const labelR = radius + 18;
        const lx = centerX + Math.cos(angle) * labelR;
        const ly = centerY + Math.sin(angle) * labelR;
        ctx!.fillStyle = 'rgba(255, 255, 255, 0.35)';
        ctx!.font = '10px -apple-system, "PingFang SC", sans-serif';
        ctx!.textAlign = 'center';
        ctx!.textBaseline = 'middle';
        ctx!.fillText(labels[i], lx, ly);
      }

      // Data polygon
      ctx!.beginPath();
      for (let i = 0; i <= n; i++) {
        const idx = i % n;
        const angle = (idx * 2 * Math.PI) / n - Math.PI / 2;
        const breathing = 1 + Math.sin(t + idx * 0.5) * 0.03;
        const r = ((values[idx] / 7) * radius) * breathing;
        const x = centerX + Math.cos(angle) * r;
        const y = centerY + Math.sin(angle) * r;
        if (i === 0) ctx!.moveTo(x, y);
        else ctx!.lineTo(x, y);
      }
      ctx!.fillStyle = 'rgba(225, 247, 57, 0.08)';
      ctx!.fill();
      ctx!.strokeStyle = 'rgba(225, 247, 57, 0.5)';
      ctx!.lineWidth = 1.2;
      ctx!.stroke();

      // Data points
      for (let i = 0; i < n; i++) {
        const angle = (i * 2 * Math.PI) / n - Math.PI / 2;
        const breathing = 1 + Math.sin(t + i * 0.5) * 0.03;
        const r = ((values[i] / 7) * radius) * breathing;
        const x = centerX + Math.cos(angle) * r;
        const y = centerY + Math.sin(angle) * r;
        ctx!.beginPath();
        ctx!.arc(x, y, 3, 0, Math.PI * 2);
        ctx!.fillStyle = '#e1f739';
        ctx!.fill();
      }

      t += 0.02;
      rafRef.current = requestAnimationFrame(draw);
    }
    rafRef.current = requestAnimationFrame(draw);

    return () => cancelAnimationFrame(rafRef.current);
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{ width: '100%', maxWidth: '400px', height: 'auto', aspectRatio: '1' }}
    />
  );
}

export default function FeatureSection() {
  return (
    <section id="features" className="relative py-40" style={{ zIndex: 2 }}>
      <div className="max-w-[1400px] mx-auto px-8">
        {/* Section Header */}
        <div className="mb-20">
          <span className="font-mono-data text-[11px] text-[#e1f739] tracking-wider">
            FEATURE ANALYSIS
          </span>
          <h2
            className="text-white font-semibold mt-3 tracking-[-0.02em]"
            style={{ fontSize: 'clamp(32px, 4vw, 48px)' }}
          >
            多维音乐画像
          </h2>
          <p
            className="mt-4 text-[15px] leading-[1.8] max-w-[540px]"
            style={{ color: 'rgba(255, 255, 255, 0.7)' }}
          >
            基于效价—唤醒度维度模型，结合温暖、紧张、希望、行动感等业务标签，
            构建可解释的音乐情绪量化指标体系
          </p>
        </div>

        {/* Three Liquid Glass Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-20">
          {/* Card 1: Applicable Spaces */}
          <LiquidGlass>
            <div className="p-8">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-8 h-8 rounded-lg bg-[#e1f739]/10 flex items-center justify-center">
                  <Radio className="w-4 h-4 text-[#e1f739]" />
                </div>
                <div>
                  <h3 className="text-white text-sm font-medium">适用空间</h3>
                  <span className="font-mono-data text-[10px] text-white/30">
                    APPLICABLE SPACES
                  </span>
                </div>
              </div>
              <div className="space-y-3">
                {sceneTemplates.map((scene, i) => (
                  <div
                    key={i}
                    className="flex items-center justify-between py-2.5 border-b border-white/5 last:border-0"
                  >
                    <span className="text-[13px]" style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                      {scene.type}
                    </span>
                    <span className="font-mono-data text-[10px] text-white/25">
                      {scene.arousal || scene.hope}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </LiquidGlass>

          {/* Card 2: Emotional Appeal */}
          <LiquidGlass>
            <div className="p-8">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-8 h-8 rounded-lg bg-[#e1f739]/10 flex items-center justify-center">
                  <Activity className="w-4 h-4 text-[#e1f739]" />
                </div>
                <div>
                  <h3 className="text-white text-sm font-medium">情感诉求</h3>
                  <span className="font-mono-data text-[10px] text-white/30">
                    EMOTIONAL APPEAL
                  </span>
                </div>
              </div>

              <div className="flex justify-center mb-4">
                <EmotionRadar />
              </div>
            </div>
          </LiquidGlass>

          {/* Card 3: Technical Parameters */}
          <LiquidGlass>
            <div className="p-8">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-8 h-8 rounded-lg bg-[#e1f739]/10 flex items-center justify-center">
                  <Layers className="w-4 h-4 text-[#e1f739]" />
                </div>
                <div>
                  <h3 className="text-white text-sm font-medium">技术参数</h3>
                  <span className="font-mono-data text-[10px] text-white/30">
                    TECHNICAL PARAMS
                  </span>
                </div>
              </div>

              <div className="space-y-4">
                {emotionDimensions.slice(0, 5).map((dim, i) => (
                  <div key={i}>
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-[12px]" style={{ color: 'rgba(255, 255, 255, 0.6)' }}>
                        {dim.label}
                      </span>
                      <span className="font-mono-data text-[10px] text-[#e1f739]">
                        {dim.range}
                      </span>
                    </div>
                    <div className="h-1 bg-white/5 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-[#e1f739]/60 to-[#e1f739] rounded-full"
                        style={{ width: `${((5 + i * 0.3) / 7) * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-6 pt-4 border-t border-white/5">
                <div className="font-mono-data text-[10px] text-white/25 mb-2">
                  LOUDNESS STANDARD
                </div>
                <div className="text-[13px]" style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                  -12 LUFS / -1 dBTP True Peak Limiting
                </div>
              </div>
            </div>
          </LiquidGlass>
        </div>

        {/* Bottom Note */}
        <div className="flex items-start gap-3 px-6 py-4 rounded-xl bg-white/[0.02] border border-white/5">
          <div className="w-1 h-1 rounded-full bg-[#e1f739] mt-2 flex-shrink-0" />
          <p className="text-[13px] leading-[1.8]" style={{ color: 'rgba(255, 255, 255, 0.5)' }}>
            上述模板为 V1.0 起始模板，必须由客户确认并随实验数据更新。
            任何单一特征（如 BPM 或大调）都不能直接等同于某一种情绪。
          </p>
        </div>
      </div>
    </section>
  );
}
