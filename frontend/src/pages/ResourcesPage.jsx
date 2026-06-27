import { useEffect, useState } from 'react';
import { Bookmark, Download, Search } from 'lucide-react';
import ToastMessage from '../components/ToastMessage.jsx';
import { lmsService } from '../services/lmsService.js';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export default function ResourcesPage() {
  const [resources, setResources] = useState([]);
  const [category, setCategory] = useState('');
  const [search, setSearch] = useState('');
  const [toast, setToast] = useState('');

  useEffect(() => {
    lmsService.resources({ category, search }).then(setResources);
  }, [category, search]);

  const bookmark = async (item) => {
    try {
      await lmsService.createBookmark({ target_type: 'resource', object_id: item.id, title: item.title, url: '/resources' });
      setToast('Resource bookmarked.');
    } catch {
      setToast('Bookmark already exists or login is required.');
    }
    setTimeout(() => setToast(''), 2500);
  };

  return (
    <div className="page-shell">
      <ToastMessage message={toast} />
      <section className="hero-panel mb-4">
        <span className="eyebrow">Material library</span>
        <h1 className="hero-title">Learning Material Library</h1>
        <p className="hero-copy">Kitoblar, maqolalar, datasetlar, kodlar va topshiriqlar uchun yagona premium kutubxona.</p>
      </section>
      <div className="glass-card p-3 p-md-4 mb-4">
        <div className="row g-3">
          <div className="col-lg">
            <label className="position-relative w-100">
              <Search className="position-absolute top-50 translate-middle-y ms-3 text-muted" size={18} />
              <input className="form-control ps-5" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Qidirish" />
            </label>
          </div>
          <div className="col-lg-4">
            <select className="form-select" value={category} onChange={(event) => setCategory(event.target.value)}>
              <option value="">Barchasi</option>
              <option value="books">Books</option>
              <option value="articles">Articles</option>
              <option value="datasets">Datasets</option>
              <option value="code">Code</option>
              <option value="presentation">Presentation</option>
              <option value="assignment">Assignment</option>
              <option value="other">Other</option>
            </select>
          </div>
        </div>
      </div>
      <div className="row g-3">
        {resources.map((item) => (
          <div className="col-md-6 col-xl-4" key={item.id}>
            <div className="glass-card h-100 p-4 d-flex flex-column">
              <span className="badge premium-badge align-self-start mb-3">{item.category}</span>
              <h2 className="h5 fw-bold">{item.title}</h2>
              <p className="text-muted flex-grow-1">{item.description}</p>
              <div className="d-flex gap-2">
                <a className="btn btn-brand flex-fill d-inline-flex align-items-center justify-content-center gap-2" href={`${API_BASE}/resources/${item.id}/download/`}><Download size={17} /> Yuklab olish</a>
                <button className="btn btn-outline-secondary d-inline-flex align-items-center gap-2" type="button" onClick={() => bookmark(item)}><Bookmark size={17} /> Save</button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
