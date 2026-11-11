import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import { BookOpen, Check, ChevronLeft, Layers3, Plus, Search, Settings2, Trash2, X, RotateCw, Keyboard } from "lucide-react";

type NavItem = "Today" | "Cards" | "Settings";
type Card = {
  id: string; cardType: string; english: string; translation: string; context: string;
  notes: string; createdAt: string; nextReviewAt: number; reviewCount: number;
};
const emptyForm = { english: "", translation: "", context: "", notes: "", cardType: "word" };

export default function App() {
  const [database, setDatabase] = useState("Connecting…");
  const [active, setActive] = useState<NavItem>("Today");
  const [cards, setCards] = useState<Card[]>([]);
  const [dueCards, setDueCards] = useState<Card[]>([]);
  const [query, setQuery] = useState("");
  const [modal, setModal] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [studyIndex, setStudyIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);

  const refresh = useCallback(async () => {
    try {
      const [all, due] = await Promise.all([
        invoke<Card[]>("list_cards", { query: "", dueOnly: false }),
        invoke<Card[]>("list_cards", { query: "", dueOnly: true }),
      ]);
      setCards(all); setDueCards(due);
    } catch (e) { setError(String(e)); }
  }, []);

  useEffect(() => {
    invoke<string>("initialize_database").then(setDatabase).catch(e => setDatabase(String(e)));
    refresh();
  }, [refresh]);

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault(); setModal(true);
      }
      if (event.key === "Escape") setModal(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const filtered = useMemo(() => cards.filter(c =>
    [c.english, c.translation, c.context].join(" ").toLowerCase().includes(query.toLowerCase())
  ), [cards, query]);

  async function createCard(event: FormEvent) {
    event.preventDefault(); setError("");
    if (!form.english.trim()) { setError("Enter a word or phrase."); return; }
    setSaving(true);
    try {
      await invoke<Card>("create_card", form);
      setForm(emptyForm); setModal(false); await refresh(); setActive("Cards");
    } catch (e) { setError(String(e)); }
    finally { setSaving(false); }
  }

  async function removeCard(id: string) {
    if (!window.confirm("Delete this card permanently?")) return;
    await invoke("delete_card", { id }); await refresh();
  }

  async function review(remembered: boolean) {
    const card = dueCards[studyIndex];
    if (!card) return;
    await invoke("review_card", { id: card.id, remembered });
    await refresh(); setStudyIndex(0); setShowAnswer(false);
  }

  const current = dueCards[studyIndex];

  return (
    <main className="shell">
      <aside className="sidebar">
        <div className="brand"><span className="brand-mark">L</span><span>lexi</span></div>
        <div className="nav-label">LIBRARY</div>
        <nav>
          <button className={active === "Today" ? "nav-item active" : "nav-item"} onClick={() => setActive("Today")}><BookOpen size={17}/>Today</button>
          <button className={active === "Cards" ? "nav-item active" : "nav-item"} onClick={() => setActive("Cards")}><Layers3 size={17}/>Cards <span className="nav-count">{cards.length}</span></button>
        </nav>
        <div className="sidebar-bottom"><button className={active === "Settings" ? "nav-item active" : "nav-item"} onClick={() => setActive("Settings")}><Settings2 size={17}/>Settings</button></div>
      </aside>

      <section className="content">
        <header className="topbar">
          <div className="breadcrumb">Workspace <span>/</span> {active}</div>
          <div className="top-actions"><span className="shortcut-hint"><Keyboard size={13}/> Ctrl K</span><div className="avatar">L</div></div>
        </header>

        <div className="page">
          <div className="eyebrow">PERSONAL VOCABULARY</div>
          {active === "Today" && <>
            <div className="heading-row"><div><h1>Good to see you.</h1><p className="subtitle">A few minutes today. A stronger vocabulary tomorrow.</p></div><button className="primary-button" onClick={() => setModal(true)}><Plus size={17}/>Add card <kbd>Ctrl K</kbd></button></div>
            <div className="stats">
              <article className="stat"><span>Due today</span><strong>{dueCards.length}</strong><small>{dueCards.length ? "Ready for a quick review" : "Nothing waiting right now"}</small></article>
              <article className="stat"><span>Total cards</span><strong>{cards.length}</strong><small>Saved on this device</small></article>
              <article className="stat"><span>Reviews completed</span><strong>{cards.reduce((n,c)=>n+c.reviewCount,0)}</strong><small>Every repetition counts</small></article>
            </div>
            {current ? <section className="study-card">
              <div className="study-top"><span>QUICK REVIEW · {studyIndex+1} OF {dueCards.length}</span><span className="type-tag">{current.cardType}</span></div>
              <h2>{current.english}</h2>
              {current.context && <p className="context-line">{current.context}</p>}
              <div className="translation">{current.translation || "Recall the meaning, then choose below."}</div>
              {current.notes && <p className="notes-line">{current.notes}</p>}
              <div className="review-actions"><button className="secondary-button" onClick={()=>review(false)}><RotateCw size={15}/>Again · 10 min</button><button className="primary-button" onClick={()=>review(true)}><Check size={16}/>Got it · 1 day</button></div>
            </section> : <section className="empty-state">
              <div className="empty-icon"><Check size={22}/></div><h2>{cards.length ? "You're all caught up." : "Start building your vocabulary"}</h2>
              <p>{cards.length ? "No cards are due. Come back later or add a useful expression from your lesson." : "Capture words and phrases from your lessons. Adding a card takes only a few seconds."}</p>
              <button className="secondary-button" onClick={()=>setModal(true)}><Plus size={16}/>Create your first card</button>
            </section>}
          </>}

          {active === "Cards" && <>
            <div className="heading-row"><div><h1>Your cards</h1><p className="subtitle">{cards.length} saved locally · search your vocabulary</p></div><button className="primary-button" onClick={()=>setModal(true)}><Plus size={17}/>Add card <kbd>Ctrl K</kbd></button></div>
            <div className="search-box"><Search size={16}/><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search words, translations, context…"/>{query && <button onClick={()=>setQuery("")} aria-label="Clear search"><X size={15}/></button>}</div>
            <div className="card-list">{filtered.map(card=><article className="word-card" key={card.id}><div className="word-main"><span className="type-tag">{card.cardType}</span><h3>{card.english}</h3><p>{card.translation || "No translation added"}</p>{card.context && <small>{card.context}</small>}</div><div className="word-meta"><span>{card.reviewCount} reviews</span><button className="icon-button danger" onClick={()=>removeCard(card.id)} aria-label="Delete card"><Trash2 size={15}/></button></div></article>)}
              {!filtered.length && <div className="list-empty">{cards.length ? "No cards match this search." : "No cards yet. Add one while you're studying."}</div>}
            </div>
          </>}

          {active === "Settings" && <>
            <div className="heading-row"><div><h1>Settings</h1><p className="subtitle">Lexi keeps your data on this device.</p></div></div>
            <section className="settings-panel"><div><strong>Local database</strong><p>SQLite · stored in your operating system's application data directory.</p></div><span className="database-path">{database}</span></section>
            <section className="settings-panel"><div><strong>Keyboard shortcut</strong><p>Open the quick-add form from anywhere in the app.</p></div><kbd>Ctrl K</kbd></section>
          </>}
          <footer className="status"><span className="status-dot"/>{database.includes("error") ? "Database unavailable" : "Local database connected"} · Your cards never leave this device</footer>
        </div>
      </section>

      {modal && <div className="modal-backdrop" onMouseDown={e=>{if(e.target===e.currentTarget)setModal(false);}}>
        <form className="modal" onSubmit={createCard}>
          <div className="modal-heading"><div><span className="eyebrow">QUICK CAPTURE</span><h2>New card</h2></div><button type="button" className="icon-button" onClick={()=>setModal(false)} aria-label="Close"><X size={17}/></button></div>
          <label>Word or phrase <span>required</span><input autoFocus value={form.english} onChange={e=>setForm({...form,english:e.target.value})} placeholder="e.g. to figure something out"/></label>
          <div className="form-row"><label>Translation<input value={form.translation} onChange={e=>setForm({...form,translation:e.target.value})} placeholder="Meaning in your language"/></label><label>Type<select value={form.cardType} onChange={e=>setForm({...form,cardType:e.target.value})}><option value="word">Word</option><option value="phrase">Phrase</option><option value="sentence">Sentence</option></select></label></div>
          <label>Context <span>optional</span><input value={form.context} onChange={e=>setForm({...form,context:e.target.value})} placeholder="Where did you encounter it?"/></label>
          <label>Notes <span>optional</span><textarea rows={2} value={form.notes} onChange={e=>setForm({...form,notes:e.target.value})} placeholder="Usage, example, nuance…"/></label>
          {error && <p className="form-error">{error}</p>}
          <div className="modal-actions"><button type="button" className="secondary-button" onClick={()=>setModal(false)}>Cancel</button><button type="submit" className="primary-button" disabled={saving}>{saving ? "Saving…" : <><Plus size={16}/>Save card</>}</button></div>
          <p className="modal-footnote">Enter to save · Esc to close</p>
        </form>
      </div>}
    </main>
  );
}
