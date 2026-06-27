import { useEffect, useState } from 'react';
import { Search } from 'lucide-react';
import { lmsService } from '../services/lmsService.js';

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  useEffect(() => {
    const timeout = setTimeout(() => {
      if (query.trim()) lmsService.search(query).then((data) => setResults(data.results));
      else setResults([]);
    }, 300);
    return () => clearTimeout(timeout);
  }, [query]);

  return (
    <div className="page-shell">
      <section className="hero-panel mb-4">
        <span className="eyebrow">Global qidiruv</span>
        <h1 className="hero-title">Barcha kontentni qidiring</h1>
        <p className="hero-copy">Kurs, dars, ma'ruza, video va resurslar bo'yicha tezkor qidiruv.</p>
      </section>
      <label className="position-relative d-block mb-4">
        <Search className="position-absolute top-50 translate-middle-y ms-3 text-muted" size={22} />
        <input className="form-control form-control-lg ps-5" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Kurs, dars, ma'ruza, video, resurs..." />
      </label>
      <div className="d-grid gap-3">
        {results.map((item) => (
          <div className="glass-card p-4" key={`${item.type}-${item.id}`}>
            <div className="d-flex justify-content-between gap-3">
              <h2 className="h6 fw-bold mb-1">{item.title}</h2>
              <span className="badge premium-badge">{item.type}</span>
            </div>
            <p className="text-muted mb-0">{item.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
