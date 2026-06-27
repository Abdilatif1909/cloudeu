import { useEffect, useMemo, useState } from 'react';
import { Bookmark, Search } from 'lucide-react';
import ToastMessage from '../components/ToastMessage.jsx';
import { lmsService } from '../services/lmsService.js';

export default function GlossaryPage() {
  const [terms, setTerms] = useState([]);
  const [search, setSearch] = useState('');
  const [letter, setLetter] = useState('');
  const [toast, setToast] = useState('');

  useEffect(() => {
    lmsService.glossary({ search }).then(setTerms);
  }, [search]);

  const letters = useMemo(() => [...new Set(terms.map((term) => term.term?.[0]?.toUpperCase()).filter(Boolean))].sort(), [terms]);
  const filteredTerms = letter ? terms.filter((term) => term.term?.toUpperCase().startsWith(letter)) : terms;

  const bookmark = async (term) => {
    try {
      await lmsService.createBookmark({ target_type: 'glossary', object_id: term.id, title: term.term, url: '/glossary' });
      setToast('Glossary term bookmarked.');
    } catch {
      setToast('Bookmark already exists or login is required.');
    }
    setTimeout(() => setToast(''), 2500);
  };

  return (
    <div className="page-shell">
      <ToastMessage message={toast} />
      <section className="hero-panel mb-4">
        <span className="eyebrow">Glossary</span>
        <h1 className="hero-title">AI tushunchalari</h1>
        <p className="hero-copy">Sun'iy intellekt terminlari, ta'riflari va kategoriyalarini tez qidiring.</p>
      </section>
      <div className="glass-card p-3 p-md-4 mb-4 position-sticky" style={{ top: 94, zIndex: 3 }}>
        <div className="d-flex flex-column flex-lg-row gap-3 align-items-lg-center justify-content-between">
          <label className="position-relative flex-grow-1">
            <Search className="position-absolute top-50 translate-middle-y ms-3 text-muted" size={18} />
            <input className="form-control ps-5" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Atama qidirish" />
          </label>
          <div className="d-flex gap-2 flex-wrap">
            <button className={`btn btn-sm ${!letter ? 'btn-brand' : 'btn-outline-secondary'}`} type="button" onClick={() => setLetter('')}>All</button>
            {letters.map((item) => (
              <button className={`btn btn-sm ${letter === item ? 'btn-brand' : 'btn-outline-secondary'}`} type="button" onClick={() => setLetter(item)} key={item}>{item}</button>
            ))}
          </div>
        </div>
      </div>
      <div className="row g-3">
        {filteredTerms.map((term) => (
          <div className="col-md-6" key={term.id}>
            <div className="glass-card h-100 p-4">
              <div className="d-flex justify-content-between gap-2">
                <h2 className="h5 fw-bold">{term.term}</h2>
                {term.category && <span className="badge premium-badge">{term.category}</span>}
              </div>
              <p className="mb-0 text-muted">{term.definition}</p>
              <button className="btn btn-outline-secondary btn-sm mt-3 d-inline-flex align-items-center gap-2" type="button" onClick={() => bookmark(term)}><Bookmark size={16} /> Bookmark</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
