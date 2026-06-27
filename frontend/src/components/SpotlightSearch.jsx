import { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { FileText, Search, Sparkles } from 'lucide-react';
import { lmsService } from '../services/lmsService.js';

export default function SpotlightSearch({ open, onClose }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [activeIndex, setActiveIndex] = useState(0);
  const inputRef = useRef(null);

  useEffect(() => {
    if (!open) return undefined;
    const timeout = setTimeout(() => inputRef.current?.focus(), 60);
    return () => clearTimeout(timeout);
  }, [open]);

  useEffect(() => {
    if (!open) return undefined;
    const handleKey = (event) => {
      if (event.key === 'Escape') onClose();
      if (event.key === 'ArrowDown') {
        event.preventDefault();
        setActiveIndex((value) => Math.min(value + 1, Math.max(results.length - 1, 0)));
      }
      if (event.key === 'ArrowUp') {
        event.preventDefault();
        setActiveIndex((value) => Math.max(value - 1, 0));
      }
      if (event.key === 'Enter' && results[activeIndex]?.url) {
        window.location.assign(results[activeIndex].url);
      }
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [activeIndex, onClose, open, results]);

  useEffect(() => {
    if (!open) return undefined;
    const timeout = setTimeout(() => {
      if (query.trim()) {
        lmsService.search(query).then((data) => {
          setResults(data.results || []);
          setActiveIndex(0);
        });
      } else {
        setResults([]);
      }
    }, 220);
    return () => clearTimeout(timeout);
  }, [open, query]);

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          className="spotlight-backdrop"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) onClose();
          }}
        >
          <motion.div className="spotlight-panel" initial={{ opacity: 0, y: -18, scale: 0.98 }} animate={{ opacity: 1, y: 0, scale: 1 }} exit={{ opacity: 0, y: -10, scale: 0.98 }}>
            <div className="position-relative">
              <Search className="position-absolute top-50 translate-middle-y ms-4 text-muted" size={22} />
              <input
                ref={inputRef}
                className="spotlight-input"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Search courses, lessons, lectures, videos..."
                aria-label="Global search"
              />
            </div>
            <div className="spotlight-results">
              {!query.trim() && (
                <div className="empty-state">
                  <div>
                    <span className="brand-mark mx-auto mb-3"><Sparkles size={22} /></span>
                    <h2 className="h5 fw-bold">Spotlight search</h2>
                    <p className="text-muted mb-0">Type anything to instantly find course content.</p>
                  </div>
                </div>
              )}
              {query.trim() && !results.length && (
                <div className="empty-state">
                  <div>
                    <h2 className="h5 fw-bold">No matching results</h2>
                    <p className="text-muted mb-0">Try a lecture title, course topic, or resource keyword.</p>
                  </div>
                </div>
              )}
              {results.map((item, index) => (
                <Link
                  className={`spotlight-item ${index === activeIndex ? 'active' : ''}`}
                  to={item.url || '/search'}
                  onClick={onClose}
                  key={`${item.type}-${item.id}`}
                >
                  <div className="d-flex align-items-start gap-3">
                    <span className="icon-chip"><FileText size={17} /></span>
                    <span className="min-w-0">
                      <span className="d-flex align-items-center gap-2 mb-1">
                        <strong>{item.title}</strong>
                        <span className="badge premium-badge">{item.type}</span>
                      </span>
                      <span className="d-block small text-muted">{item.description}</span>
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
