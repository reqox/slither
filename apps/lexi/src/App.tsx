import { useEffect, useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import { BookOpen, Layers3, Plus, RotateCw, Search, Settings2 } from "lucide-react";

type NavItem = "Today" | "Cards" | "Settings";

export default function App() {
  const [database, setDatabase] = useState("Initializing local database…");
  const [active, setActive] = useState<NavItem>("Today");

  useEffect(() => {
    invoke<string>("initialize_database")
      .then(setDatabase)
      .catch((error: unknown) => setDatabase(`Database error: ${String(error)}`));
  }, []);

  return (
    <main className="shell">
      <aside className="sidebar">
        <div className="brand"><span className="brand-mark">L</span><span>lexi</span></div>
        <div className="nav-label">LIBRARY</div>
        <nav>
          <button className={active === "Today" ? "nav-item active" : "nav-item"} onClick={() => setActive("Today")}><BookOpen size={17} />Today</button>
          <button className={active === "Cards" ? "nav-item active" : "nav-item"} onClick={() => setActive("Cards")}><Layers3 size={17} />Cards</button>
        </nav>
        <div className="sidebar-bottom">
          <button className={active === "Settings" ? "nav-item active" : "nav-item"} onClick={() => setActive("Settings")}><Settings2 size={17} />Settings</button>
        </div>
      </aside>
      <section className="content">
        <header className="topbar">
          <div className="breadcrumb">Workspace <span>/</span> {active}</div>
          <div className="top-actions"><button className="icon-button" aria-label="Search"><Search size={17} /></button><div className="avatar">V</div></div>
        </header>
        <div className="page">
          <div className="eyebrow">PERSONAL VOCABULARY</div>
          <div className="heading-row"><div><h1>{active === "Today" ? "Good to see you." : active}</h1><p className="subtitle">Build your vocabulary, one useful phrase at a time.</p></div><button className="primary-button"><Plus size={17} />Add card <kbd>⌘ K</kbd></button></div>
          <div className="stats">
            <article className="stat"><span>Due today</span><strong>—</strong><small>Ready when you are</small></article>
            <article className="stat"><span>Total cards</span><strong>0</strong><small>Your vocabulary starts here</small></article>
            <article className="stat"><span>Study streak</span><strong>0 <em>days</em></strong><small>A little every day adds up</small></article>
          </div>
          <section className="empty-state">
            <div className="empty-icon"><RotateCw size={22} /></div>
            <h2>Your next review starts here</h2>
            <p>Add a word or phrase while studying. Keep it quick — you can return to your lesson in seconds.</p>
            <button className="secondary-button"><Plus size={16} />Create your first card</button>
          </section>
          <footer className="status"><span className="status-dot" />Local database · {database}</footer>
        </div>
      </section>
    </main>
  );
}
