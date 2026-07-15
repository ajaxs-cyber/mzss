import { Music, Github, ExternalLink } from 'lucide-react';

export default function FooterSection() {
  return (
    <footer className="relative py-20 border-t border-white/5" style={{ zIndex: 2 }}>
      <div className="max-w-[1400px] mx-auto px-8">
        <div className="flex flex-col md:flex-row items-start justify-between gap-12">
          {/* Brand */}
          <div className="max-w-[360px]">
            <div className="flex items-center gap-2.5 mb-4">
              <div className="w-7 h-7 rounded-full bg-[#e1f739]/20 flex items-center justify-center">
                <Music className="w-3.5 h-3.5 text-[#e1f739]" />
              </div>
              <span className="text-white font-semibold text-sm">觅知音</span>
            </div>
            <p className="text-[13px] leading-[1.8]" style={{ color: 'rgba(255, 255, 255, 0.5)' }}>
              音乐—场景量化匹配机制技术规范 V1.0。
              从客户场景需求到音乐特征工程约束的可解释推荐框架。
            </p>
          </div>

          {/* Links */}
          <div className="flex gap-16">
            <div>
              <div className="font-mono-data text-[10px] text-white/30 mb-4">
                RESOURCES
              </div>
              <div className="space-y-2.5">
                <a
                  href="https://github.com/ajaxs-cyber/my-music-storage"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 text-[13px] hover:text-[#e1f739] transition-colors"
                  style={{ color: 'rgba(255, 255, 255, 0.6)' }}
                >
                  <Github className="w-3 h-3" />
                  音乐资源库
                </a>
                <a
                  href="https://github.com/ajaxs-cyber/mzss"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 text-[13px] hover:text-[#e1f739] transition-colors"
                  style={{ color: 'rgba(255, 255, 255, 0.6)' }}
                >
                  <Github className="w-3 h-3" />
                  MZSS 项目
                </a>
              </div>
            </div>

            <div>
              <div className="font-mono-data text-[10px] text-white/30 mb-4">
                DEPLOYMENT
              </div>
              <div className="space-y-2.5">
                <a
                  href="https://smzz.pythonanywhere.com/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 text-[13px] hover:text-[#e1f739] transition-colors"
                  style={{ color: 'rgba(255, 255, 255, 0.6)' }}
                >
                  <ExternalLink className="w-3 h-3" />
                  PythonAnywhere
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* Copyright */}
        <div className="mt-16 pt-6 border-t border-white/5 flex flex-col md:flex-row items-center justify-between gap-4">
          <span className="font-mono-data text-[10px] text-white/20">
            &copy; 2026 MZSS PROJECT. ALL RIGHTS RESERVED.
          </span>
          <span className="font-mono-data text-[10px] text-white/15">
            BUILT WITH REACT + TAILWIND + WEBGL
          </span>
        </div>
      </div>
    </footer>
  );
}
