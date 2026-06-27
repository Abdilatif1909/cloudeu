import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Bookmark, ExternalLink, Trash2 } from 'lucide-react';
import ToastMessage from '../components/ToastMessage.jsx';
import { lmsService } from '../services/lmsService.js';

export default function BookmarksPage() {
  const [bookmarks, setBookmarks] = useState([]);
  const [toast, setToast] = useState('');

  const loadBookmarks = () => lmsService.bookmarks().then(setBookmarks);

  useEffect(() => {
    loadBookmarks();
  }, []);

  const removeBookmark = async (id) => {
    await lmsService.deleteBookmark(id);
    setToast('Bookmark removed.');
    loadBookmarks();
    setTimeout(() => setToast(''), 2400);
  };

  return (
    <div className="page-shell">
      <ToastMessage message={toast} />
      <section className="hero-panel mb-4">
        <span className="eyebrow"><Bookmark size={16} /> Saved learning</span>
        <h1 className="hero-title">My Bookmarks</h1>
        <p className="hero-copy">Your saved lectures, glossary terms, videos and resources in one polished workspace.</p>
      </section>
      <div className="row g-3">
        {bookmarks.map((item) => (
          <div className="col-md-6 col-xl-4" key={item.id}>
            <div className="glass-card h-100 p-4 d-flex flex-column">
              <span className="badge premium-badge align-self-start mb-3">{item.content_type_label}</span>
              <h2 className="h5 fw-bold">{item.title}</h2>
              <div className="mt-auto d-flex gap-2 pt-4">
                {item.url && <Link className="btn btn-brand flex-fill d-inline-flex align-items-center justify-content-center gap-2" to={item.url}><ExternalLink size={17} /> Open</Link>}
                <button className="btn btn-outline-secondary d-inline-flex align-items-center gap-2" type="button" onClick={() => removeBookmark(item.id)}><Trash2 size={17} /> Delete</button>
              </div>
            </div>
          </div>
        ))}
        {!bookmarks.length && (
          <div className="col-12">
            <div className="empty-state">
              <div>
                <span className="brand-mark mx-auto mb-3"><Bookmark size={22} /></span>
                <h2 className="h5 fw-bold">No bookmarks yet</h2>
                <p className="text-muted mb-0">Save lectures, videos and terms to build your personal learning queue.</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
