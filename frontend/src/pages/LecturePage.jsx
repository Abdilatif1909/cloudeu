import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Bookmark, Download, Maximize2, Minus, Plus, Search, SkipBack, SkipForward } from 'lucide-react';
import Breadcrumbs from '../components/Breadcrumbs.jsx';
import LoadingSkeleton from '../components/LoadingSkeleton.jsx';
import ToastMessage from '../components/ToastMessage.jsx';
import { lmsService } from '../services/lmsService.js';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export default function LecturePage() {
  const { lectureId } = useParams();
  const [lecture, setLecture] = useState(null);
  const [nav, setNav] = useState({});
  const [pdfProgress, setPdfProgress] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [zoom, setZoom] = useState(100);
  const [pdfSearch, setPdfSearch] = useState('');
  const [note, setNote] = useState(null);
  const [noteContent, setNoteContent] = useState('');
  const [toast, setToast] = useState('');

  useEffect(() => {
    lmsService.lecture(lectureId).then(setLecture);
    lmsService.lectureNavigation(lectureId).then(setNav);
    lmsService.pdfProgress({ lecture: lectureId }).then((items) => {
      const saved = items[0];
      if (saved) {
        setPdfProgress(saved);
        setPage(saved.current_page || 1);
        setTotalPages(saved.total_pages || 1);
        setZoom(Math.round((saved.zoom || 1) * 100));
      }
    }).catch(() => {});
    lmsService.notes({ lecture: lectureId }).then((items) => {
      const saved = items[0];
      if (saved) {
        setNote(saved);
        setNoteContent(saved.content || '');
      }
    }).catch(() => {});
  }, [lectureId]);

  useEffect(() => {
    if (!lecture) return undefined;
    const timeout = setTimeout(async () => {
      const payload = {
        lecture: Number(lectureId),
        current_page: page,
        total_pages: totalPages,
        zoom: zoom / 100,
      };
      try {
        const saved = pdfProgress
          ? await lmsService.updatePdfProgress(pdfProgress.id, payload)
          : await lmsService.savePdfProgress(payload);
        setPdfProgress(saved);
      } catch {
        // Anonymous readers can still use the embedded PDF reader.
      }
    }, 700);
    return () => clearTimeout(timeout);
  }, [lecture, lectureId, page, totalPages, zoom]);

  useEffect(() => {
    if (!lecture || !noteContent.trim()) return undefined;
    const timeout = setTimeout(async () => {
      try {
        const payload = {
          course: lecture.course_id,
          lesson: lecture.lesson,
          lecture: lecture.id,
          title: `${lecture.title} notes`,
          content: noteContent,
        };
        const saved = note ? await lmsService.updateNote(note.id, payload) : await lmsService.createNote(payload);
        setNote(saved);
      } catch {
        // Notes require authentication; keep local editing responsive.
      }
    }, 900);
    return () => clearTimeout(timeout);
  }, [lecture, note, noteContent]);

  const bookmark = async () => {
    try {
      await lmsService.createBookmark({
        target_type: 'lecture',
        object_id: lecture.id,
        title: lecture.title,
        url: `/lectures/${lecture.id}`,
      });
      setToast('Lecture bookmarked.');
    } catch {
      setToast('Bookmark already exists or login is required.');
    }
    setTimeout(() => setToast(''), 2500);
  };

  if (!lecture) return <div className="page-shell"><LoadingSkeleton /></div>;

  const pdfSrc = `${API_BASE}/lecture-materials/${lecture.id}/preview/#page=${page}&zoom=${zoom}${pdfSearch ? `&search=${encodeURIComponent(pdfSearch)}` : ''}`;

  return (
    <div className="page-shell">
      <ToastMessage message={toast} />
      <Breadcrumbs items={[{ label: lecture.lesson_title, active: true }]} />
      <div className="row g-4">
        <div className="col-lg-8">
          <span className="eyebrow">Lecture reader</span>
          <h1 className="h2 fw-bold mt-3">{lecture.lecture_number}. {lecture.title}</h1>
          <p className="text-muted">{lecture.description}</p>
          <div className="glass-card mb-3">
            <div className="card-body pdf-reader-toolbar">
              <div className="d-flex flex-wrap gap-2 align-items-center">
                <button className="btn btn-outline-secondary btn-sm" type="button" onClick={() => setPage((value) => Math.max(value - 1, 1))} aria-label="Previous page"><SkipBack size={16} /></button>
                <input className="form-control form-control-sm" style={{ width: 86 }} type="number" min="1" value={page} onChange={(event) => setPage(Math.max(Number(event.target.value), 1))} />
                <span className="text-muted small">of</span>
                <input className="form-control form-control-sm" style={{ width: 86 }} type="number" min="1" value={totalPages} onChange={(event) => setTotalPages(Math.max(Number(event.target.value), 1))} />
                <button className="btn btn-outline-secondary btn-sm" type="button" onClick={() => setPage((value) => Math.min(value + 1, totalPages))} aria-label="Next page"><SkipForward size={16} /></button>
                <button className="btn btn-outline-secondary btn-sm" type="button" onClick={() => setZoom((value) => Math.max(value - 10, 50))} aria-label="Zoom out"><Minus size={16} /></button>
                <span className="small">{zoom}%</span>
                <button className="btn btn-outline-secondary btn-sm" type="button" onClick={() => setZoom((value) => Math.min(value + 10, 200))} aria-label="Zoom in"><Plus size={16} /></button>
                <label className="position-relative flex-grow-1">
                  <Search className="position-absolute top-50 translate-middle-y ms-3 text-muted" size={16} />
                  <input className="form-control form-control-sm ps-5" value={pdfSearch} onChange={(event) => setPdfSearch(event.target.value)} placeholder="Search in PDF" />
                </label>
                <button className="btn btn-outline-secondary btn-sm" type="button" onClick={() => document.querySelector('#lecture-pdf')?.requestFullscreen?.()} aria-label="Fullscreen"><Maximize2 size={16} /></button>
              </div>
              <div className="progress mt-3" style={{ height: 6 }}>
                <div className="progress-bar" style={{ width: `${Math.min((page / totalPages) * 100, 100)}%` }} />
              </div>
            </div>
          </div>
          <iframe id="lecture-pdf" className="w-100 media-frame" style={{ height: 640 }} src={pdfSrc} title={lecture.title} />
          <div className="glass-card mt-4">
            <div className="card-body">
              <h2 className="h5 fw-bold">Personal notes</h2>
              <textarea className="form-control" rows="8" value={noteContent} onChange={(event) => setNoteContent(event.target.value)} placeholder="Write notes for this lecture. Changes auto-save when logged in." />
              {note && <a className="btn btn-outline-secondary btn-sm mt-2" href={`${API_BASE}/notes/${note.id}/export-pdf/`}>Export note PDF</a>}
            </div>
          </div>
        </div>
        <aside className="col-lg-4">
          <div className="glass-card position-sticky" style={{ top: 112 }}>
            <div className="card-body">
              {lecture.cover_image && <img className="img-fluid rounded mb-3" src={lecture.cover_image} alt={lecture.title} />}
              <h2 className="h5 fw-bold">Reader tools</h2>
              <div className="resource-row">
                <span className="text-muted">Reading progress</span>
                <strong>{Math.min(Math.round((page / totalPages) * 100), 100)}%</strong>
              </div>
              <div className="resource-row"><span className="text-muted">O'qish vaqti</span><strong>{lecture.estimated_reading_time} daqiqa</strong></div>
              <div className="resource-row"><span className="text-muted">Ko'rishlar</span><strong>{lecture.view_count}</strong></div>
              <div className="resource-row mb-3"><span className="text-muted">Yuklab olishlar</span><strong>{lecture.download_count}</strong></div>
              <div className="mb-3">
                <div className="small fw-bold text-muted mb-2">Table of contents</div>
                {['Overview', 'Key terms', 'Examples', 'Summary'].map((item, index) => (
                  <button className="resource-row border-0 bg-transparent w-100 text-start" type="button" onClick={() => setPage(Math.min(index + 1, totalPages))} key={item}>
                    <span>{item}</span>
                    <span className="badge premium-badge">p.{Math.min(index + 1, totalPages)}</span>
                  </button>
                ))}
              </div>
              <a className="btn btn-brand w-100 mb-2 d-inline-flex align-items-center justify-content-center gap-2" href={`${API_BASE}/lecture-materials/${lecture.id}/download/`}><Download size={17} /> PDF yuklab olish</a>
              <button className="btn btn-outline-secondary w-100 mb-2 d-inline-flex align-items-center justify-content-center gap-2" type="button" onClick={bookmark}><Bookmark size={17} /> Bookmark</button>
              <div className="d-flex gap-2">
                {nav.previous && <Link className="btn btn-outline-secondary flex-fill" to={`/lectures/${nav.previous.id}`}>Oldingi</Link>}
                {nav.next && <Link className="btn btn-outline-secondary flex-fill" to={`/lectures/${nav.next.id}`}>Keyingi</Link>}
              </div>
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}
