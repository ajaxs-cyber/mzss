export default function Navigation() {
  return (
    <header className="topbar">
      <a className="brand" href="#top" aria-label="觅知音首页">
        <span className="brand-mark">M</span>
        <span>觅知音</span>
      </a>
      <div className="topbar-center">
        <span className="online-dot" />
        匹配机制 V1.0
        <span className="divider" />
        可解释推荐
      </div>
      <a href="https://github.com/ajaxs-cyber/mzss" className="help-button" target="_blank" rel="noopener noreferrer">
        GitHub <span>↗</span>
      </a>
    </header>
  );
}
