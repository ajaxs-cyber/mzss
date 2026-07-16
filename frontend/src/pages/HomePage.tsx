import { useState, useMemo, type CSSProperties } from 'react';
import { computeEmotionMatch, runMatching, type TargetProfile, type MatchResult, type EmotionRange } from '@/lib/matching';
import { tracks } from '@/data/musicLibrary';
import type { Track } from '@/data/musicLibrary';

/* ========================== Constants ========================== */

const STEPS = ['场景需求', '情绪画像', '候选推荐'];

const INDUSTRIES = ['美妆', '文创', '医疗', '公益', '零售', '教育', '宠物'];
const TASKS = ['浏览体验', '阅读详情', '加入购物车', '购买决策', '捐赠决策'];
const BRAND_TAGS = ['自然', '温暖', '精致', '年轻', '可靠', '活力', '传统', '清爽', '稳重'];
const PLACEMENTS = ['首屏', '浏览过程', '结算前', '线下空间'];

const DIM_LABELS: Array<{ key: 'valence' | 'arousal' | 'warmth' | 'tension' | 'hope' | 'motivation' | 'intrusion'; cn: string; hint: string; color: string }> = [
  { key: 'valence', cn: '效价', hint: '负面 → 积极', color: '#e5677c' },
  { key: 'arousal', cn: '唤醒度', hint: '平静 → 激昂', color: '#f0a34e' },
  { key: 'warmth', cn: '温暖感', hint: '疏离 → 亲近', color: '#d99363' },
  { key: 'tension', cn: '紧张感', hint: '放松 → 压迫', color: '#8d79bd' },
  { key: 'hope', cn: '希望感', hint: '停滞 → 向上', color: '#78a77a' },
  { key: 'motivation', cn: '行动感', hint: '静默 → 驱动', color: '#5a9aa3' },
  { key: 'intrusion', cn: '侵入感', hint: '无干扰 → 强干扰', color: '#a08a7c' },
];

function defaultProfile(): TargetProfile {
  return {
    valence: { min: 0.45, max: 0.75 },
    arousal: { min: 0.25, max: 0.55 },
    warmth: { min: 0.45, max: 0.70 },
    tension: { min: 0.05, max: 0.30 },
    hope: { min: 0.40, max: 0.70 },
    motivation: { min: 0.25, max: 0.55 },
    intrusion: { min: 0.0, max: 0.30 },
    constraints: { allowLyrics: false, allowVocal: true, minBpm: 60, maxBpm: 150 },
  };
}

/* ========================== Sub-components ========================== */

function StepIndicator({ current }: { current: number }) {
  return (
    <nav className="steps">
      {STEPS.map((name, i) => (
        <button
          key={name}
          className={i === current ? 'step active' : i < current ? 'step complete' : 'step'}
          onClick={() => {}}
          type="button"
        >
          <b>{i < current ? '✓' : `0${i + 1}`}</b>
          <span>{name}</span>
        </button>
      ))}
    </nav>
  );
}

function ToggleChip({ label, selected, onClick }: { label: string; selected: boolean; onClick: () => void }) {
  return (
    <button onClick={onClick} className={selected ? 'tag selected' : 'tag'} type="button">
      {label}
    </button>
  );
}

/* ========================== Step 1: Scene Input ========================== */

function StepSceneInput({
  form, update, toggleBrand,
}: {
  form: any; update: (k: string, v: string | boolean) => void; toggleBrand: (t: string) => void;
}) {
  return (
    <div className="content-grid input-stage">
      <section className="form-card panel">
        <div className="panel-heading">
          <div>
            <span className="kicker">SCENE BRIEF</span>
            <h2>描述你的场景</h2>
          </div>
          <span className="required">* 必填项</span>
        </div>
        <div className="form-grid">
          <label className="wide">
            项目名称
            <input value={form.projectName} onChange={e => update('projectName', e.target.value)} placeholder="例：绒光腮红" />
          </label>
          <label>
            所属行业
            <select value={form.industry} onChange={e => update('industry', e.target.value)}>
              <option value="">请选择</option>
              {INDUSTRIES.map(ind => <option key={ind}>{ind}</option>)}
            </select>
          </label>
          <label>
            用户当前任务
            <select value={form.task} onChange={e => update('task', e.target.value)}>
              <option value="">请选择</option>
              {TASKS.map(t => <option key={t}>{t}</option>)}
            </select>
          </label>
          <label className="wide">
            内容主题与关键词
            <input value={form.keywords} onChange={e => update('keywords', e.target.value)} placeholder="例：自然妆感、柔和粉色、日常通勤" />
          </label>
          <label>
            目标用户
            <input value={form.ageRange} onChange={e => update('ageRange', e.target.value)} placeholder="例：18–30岁年轻女性" />
          </label>
          <label>
            播放位置
            <select value={form.placement} onChange={e => update('placement', e.target.value)}>
              <option value="">请选择</option>
              {PLACEMENTS.map(p => <option key={p}>{p}</option>)}
            </select>
          </label>
        </div>
        <div className="tag-section">
          <span>希望传递的品牌感受</span>
          <div className="tag-list">
            {BRAND_TAGS.map(tag => (
              <ToggleChip key={tag} label={tag} selected={form.brandTags.includes(tag)} onClick={() => toggleBrand(tag)} />
            ))}
          </div>
        </div>
        <div className="preference-row">
          <div><span>歌词</span><small>优先纯音乐</small></div>
          <button className={form.allowLyrics ? 'toggle' : 'toggle on'} onClick={() => update('allowLyrics', !form.allowLyrics)} aria-label="切换歌词"><i /></button>
          <div><span>人声</span><small>允许含人声</small></div>
          <button className={form.allowVocal ? 'toggle on' : 'toggle'} onClick={() => update('allowVocal', !form.allowVocal)} aria-label="切换人声"><i /></button>
        </div>
      </section>
      <aside className="insight-card">
        <span className="kicker">WHY THIS MATTERS</span>
        <h3>不只问"提高销量"</h3>
        <p>系统需要理解场景真正需要的是热烈感、信任感，还是陪伴感。</p>
        <div className="insight-points">
          <div><b>01</b><span>音乐表达情绪</span></div>
          <div><b>02</b><span>用户诱发情绪</span></div>
          <div><b>03</b><span>场景目标情绪</span></div>
        </div>
        <p className="tiny">第一版以"音乐表达情绪"为自动分析对象，并通过试听反馈持续校准。</p>
      </aside>
    </div>
  );
}

/* ========================== Step 2: Emotion Profile ========================== */

function StepEmotionProfile({
  profile, setProfile,
}: {
  profile: TargetProfile; setProfile: (p: TargetProfile) => void;
}) {
  type DimKey = 'valence' | 'arousal' | 'warmth' | 'tension' | 'hope' | 'motivation' | 'intrusion';

  const updateDim = (key: DimKey, field: 'min' | 'max', raw: number) => {
    const next = { ...profile[key], [field]: raw };
    if (field === 'min' && raw > next.max) next.max = raw;
    if (field === 'max' && raw < next.min) next.min = raw;
    setProfile({ ...profile, [key]: next });
  };

  const profileScore = useMemo(() => {
    const dims = Object.values(profile).filter(v => v && typeof v === 'object' && 'min' in v) as EmotionRange[];
    if (dims.length === 0) return 0;
    return Math.round(dims.reduce((sum, d) => sum + (d.min + d.max) / 2, 0) / dims.length * 10) / 10;
  }, [profile]);

  return (
    <div className="profile-layout">
      <section className="profile-card panel">
        <div className="panel-heading">
          <div>
            <span className="kicker">TARGET EMOTION PROFILE</span>
            <h2>目标情绪画像</h2>
            <p>拖动滑杆调节每维度的目标区间，下方实时预览匹配效果。</p>
          </div>
          <div className="profile-badge">
            <b>{profileScore.toFixed(1)}</b>
            <span>综合氛围</span>
          </div>
        </div>
        <div className="sliders">
          {DIM_LABELS.map(dim => {
            const range = profile[dim.key] as EmotionRange;
            return (
              <div className="slider-row" key={dim.key} style={{ '--accent': dim.color } as CSSProperties}>
                <div className="slider-label">
                  <b>{dim.cn}</b>
                  <span>{dim.hint}</span>
                </div>
                <div className="range-controls">
                  <input
                    type="range" min="0" max="1" step="0.05"
                    value={range.min}
                    onChange={e => updateDim(dim.key, 'min', Number(e.target.value))}
                    aria-label={`${dim.cn} 最低值`}
                  />
                  <input
                    type="range" min="0" max="1" step="0.05"
                    value={range.max}
                    onChange={e => updateDim(dim.key, 'max', Number(e.target.value))}
                    aria-label={`${dim.cn} 最高值`}
                  />
                </div>
                <output>{(range.min * 7).toFixed(1)}–{(range.max * 7).toFixed(1)}</output>
              </div>
            );
          })}
        </div>
        <div className="constraint-card">
          <div>
            <span className="kicker">PLAYBACK CONSTRAINTS</span>
            <p>
              {profile.constraints.allowLyrics ? '允许歌词' : '纯音乐优先'}
              {' · '}
              干扰风险 ≤ {profile.intrusion.max > 1 ? '7.0' : (profile.intrusion.max * 7).toFixed(1)}
              {' · '}
              BPM {profile.constraints.minBpm}–{profile.constraints.maxBpm}
              {' · '}
              用户点击播放
            </p>
          </div>
        </div>
      </section>
      <aside className="method-card">
        <span className="kicker">INTERPRETABLE BY DESIGN</span>
        <h3>音乐不是一个情绪标签</h3>
        <p>效价与唤醒度构成基础坐标，温暖、希望、行动感由多项线索与人工试听共同确定。</p>
        <div className="formula">
          <span>FinalScore</span><b>=</b>
          <span>λ × AI</span><i>+</i>
          <span>(1−λ) × 人工</span>
        </div>
        <div className="method-note">
          <b>实时预览</b>
          <p>下方展示当前画像对曲库中曲目的匹配度。</p>
          <div className="mt-4 space-y-2">
            {tracks.slice(0, 4).map(t => {
              const r = computeEmotionMatch(t, profile);
              return (
                <div key={t.id} className="flex items-center gap-2">
                  <span className="text-xs w-24 truncate text-left">{t.title}</span>
                  <div className="flex-1 h-1.5 rounded-full bg-white/10 overflow-hidden">
                    <div className="h-full rounded-full bg-[#78a77a] transition-all" style={{ width: `${Math.round(r.total * 100)}%` }} />
                  </div>
                  <span className="text-[10px] w-10 text-right">{Math.round(r.total * 100)}%</span>
                </div>
              );
            })}
          </div>
        </div>
      </aside>
    </div>
  );
}

/* ========================== Step 3: Results ========================== */

function StepResults({
  results,
}: {
  results: MatchResult[];
}) {
  const [activeIdx, setActiveIdx] = useState(0);
  const [playing, setPlaying] = useState(false);
  const active = results[activeIdx];

  if (!active) {
    return (
      <section className="results-stage">
        <div className="text-center py-20 text-[#667071]">
          <p className="text-lg">没有符合约束的曲目</p>
          <p className="text-sm mt-2">请放宽情绪区间或播放限制后重试</p>
        </div>
      </section>
    );
  }

  const track = active.track;
  const colors = ['#e5677c', '#f0a34e', '#d99363', '#8d79bd', '#78a77a', '#5a9aa3', '#a08a7c'];

  return (
    <section className="results-stage">
      <div className="results-heading">
        <div>
          <span className="kicker">MATCHED FOR YOUR SCENE</span>
          <h2>为当前场景找到 <em>{results.length}</em> 首候选</h2>
          <p>已排除版权状态不明、高干扰风险及不适宜歌词内容的曲目。</p>
        </div>
      </div>
      <div className="result-grid">
        <div className="track-list">
          {results.map((r, i) => (
            <button
              key={r.track.id}
              className={i === activeIdx ? 'track-card active' : 'track-card'}
              onClick={() => { setActiveIdx(i); setPlaying(false); }}
            >
              <span className="track-index">{String(i + 1).padStart(2, '0')}</span>
              <span className="art"><i /></span>
              <span className="track-text">
                <b>{r.track.title}</b>
                <small>{r.track.genre} · {r.track.bpm} BPM</small>
              </span>
              <span className="score">
                <b>{Math.round(r.totalScore * 100)}</b>
                <small>匹配分</small>
              </span>
            </button>
          ))}
        </div>

        {/* Track Detail Panel */}
        <article className="track-detail panel">
          <div className="track-detail-header">
            <div>
              <span className="kicker">RECOMMENDED #{String(activeIdx + 1).padStart(2, '0')}</span>
              <h2>{track.title}</h2>
              <p>{track.artist} <span className="mini-dot" /> {track.genre} <span className="mini-dot" /> {track.duration}</p>
            </div>
            <span className="confidence" style={{ background: track.confidence > 0.9 ? '#edf4ee' : '#fdf3e7', color: track.confidence > 0.9 ? '#50816a' : '#b87a3a' }}>
              {track.confidence > 0.9 ? '高置信度' : '已校准'}
            </span>
          </div>

          {/* Player */}
          <div className="player">
            <button onClick={() => setPlaying(!playing)} aria-label={playing ? '暂停' : '播放'}>
              {playing ? 'Ⅱ' : '▶'}
            </button>
            <div className="wave">
              {Array.from({ length: 34 }).map((_, i) => (
                <i key={i} style={{ height: `${18 + ((i * 23) % 55)}%` }} />
              ))}
            </div>
            <span>{track.duration}</span>
          </div>

          {/* Emotion Table */}
          <div className="emotion-table">
            <div className="emotion-table-head">
              <span>情绪坐标</span><span>得分</span><span>目标区间</span>
            </div>
            {DIM_LABELS.map((dim, idx) => {
              const detail = active.details[dim.key];
              const trackVal = track[dim.key as keyof Track] as number;
              return (
                <div className="emotion-item" key={dim.key}>
                  <span>
                    <i style={{ background: colors[idx % colors.length] }} />
                    {dim.cn}
                  </span>
                  <b>{((trackVal) * 7).toFixed(1)}</b>
                  <em>{detail?.target || '–'}</em>
                </div>
              );
            })}
          </div>

          {/* Feature Chips */}
          <div className="feature-chips">
            <span>BPM {track.bpm}</span>
            <span>{track.key}</span>
            <span>LUFS {track.lufsValue}</span>
            <span>干扰风险 {(track.intrusion * 7).toFixed(1)}</span>
            <span>人声 {Math.round(track.vocalProbability * 100)}%</span>
          </div>

          {/* Reason */}
          <div className="reason">
            <span>可解释特征</span>
            {track.explanation?.map((line, i) => (
              <p key={i}>{line}</p>
            ))}
          </div>

          {/* Playback Suggestion */}
          <div className="playback-suggestion">
            <b>播放建议</b>
            <span>默认静音，由用户点击播放；音量 20%–30%。</span>
          </div>
        </article>
      </div>
    </section>
  );
}

/* ========================== Main HomePage ========================== */

export default function HomePage() {
  const [step, setStep] = useState(0);
  const [profile, setProfile] = useState<TargetProfile>(defaultProfile());

  const [form, setForm] = useState({
    projectName: '',
    industry: '',
    task: '',
    keywords: '',
    ageRange: '',
    placement: '',
    brandTags: [] as string[],
    allowLyrics: false,
    allowVocal: true,
  });

  const update = (k: string, v: any) => setForm(prev => ({ ...prev, [k]: v }));
  const toggleBrand = (tag: string) => {
    setForm(prev => ({
      ...prev,
      brandTags: prev.brandTags.includes(tag) ? prev.brandTags.filter(t => t !== tag) : [...prev.brandTags, tag],
    }));
  };

  const results = useMemo(() => runMatching(profile), [profile]);

  return (
    <main>
      {/* Hero */}
      <section className="hero" id="top">
        <div className="eyebrow"><span />MUSIC × SCENE INTELLIGENCE</div>
        <h1>让每一段声音，<br /><em>恰好抵达</em> 场景。</h1>
        <p>从声学特征到人工校准，以可解释的方式，为品牌与公益场景找到合适的音乐。</p>
        <div className="hero-rule">
          <span>声学特征</span><i>→</i><span>情绪初判</span><i>→</i><span>人工校准</span><i>→</i><strong>场景匹配</strong><i>→</i><span>行为迭代</span>
        </div>
      </section>

      {/* Workflow */}
      <section className="workflow" aria-label="音乐场景匹配流程">
        <StepIndicator current={step} />

        {step === 0 && (
          <StepSceneInput form={form} update={update} toggleBrand={toggleBrand} />
        )}

        {step === 1 && (
          <StepEmotionProfile profile={profile} setProfile={setProfile} />
        )}

        {step === 2 && (
          <StepResults results={results} />
        )}

        {/* Navigation Buttons */}
        <div className="mt-8 flex items-center justify-between max-w-[680px] mx-auto">
          <button
            onClick={() => setStep(s => Math.max(0, s - 1))}
            disabled={step === 0}
            className="rounded-lg border border-[#b4c2ba] px-5 py-2.5 text-sm text-[#53605f] transition-all hover:bg-white/50 disabled:opacity-30 disabled:cursor-not-allowed"
          >
            ← 返回上一步
          </button>
          <div className="text-xs text-[#98a19e]">
            {step + 1} / {STEPS.length}
          </div>
          {step < STEPS.length - 1 ? (
            <button
              onClick={() => setStep(s => s + 1)}
              className="primary-button w-auto px-6"
            >
              {step === 0 ? '生成目标情绪画像' : '查看匹配结果'} <span>→</span>
            </button>
          ) : (
            <button
              onClick={() => setStep(0)}
              className="rounded-lg border border-[#b4c2ba] px-5 py-2.5 text-sm text-[#315f52] transition-all hover:bg-white/50"
            >
              重新匹配
            </button>
          )}
        </div>
      </section>

      {/* Footer */}
      <footer>
        <span>觅知音 · 声景匹配机制 V1.0</span>
        <span>不替代人的感受判断，只让选择更有依据。</span>
        <span>© 2026</span>
      </footer>
    </main>
  );
}
