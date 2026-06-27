import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Bookmark, CheckCircle2, Download } from 'lucide-react';
import Breadcrumbs from '../components/Breadcrumbs.jsx';
import LoadingSkeleton from '../components/LoadingSkeleton.jsx';
import ToastMessage from '../components/ToastMessage.jsx';
import { lmsService } from '../services/lmsService.js';
import { mediaUrl } from '../utils/mediaUrl.js';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1';

const difficultyLabels = {
  easy: 'Easy',
  medium: 'Medium',
  hard: 'Hard',
};

export default function PracticePage() {
  const { practiceId } = useParams();
  const [practice, setPractice] = useState(null);
  const [files, setFiles] = useState({});
  const [toast, setToast] = useState('');

  useEffect(() => {
    lmsService.practice(practiceId).then(setPractice);
    lmsService.practiceFiles(practiceId).then(setFiles);
  }, [practiceId]);

  if (!practice) return <div className="page-shell"><LoadingSkeleton /></div>;
  const practicePdfUrl = mediaUrl(practice.pdf_file);

  const showToast = (message) => {
    setToast(message);
    setTimeout(() => setToast(''), 2500);
  };

  const bookmark = async () => {
    try {
      await lmsService.createBookmark({ target_type: 'practice', object_id: practice.id, title: practice.title, url: `/practices/${practice.id}` });
      showToast('Practice bookmarked.');
    } catch {
      showToast('Bookmark already exists or login is required.');
    }
  };

  const markCompleted = async () => {
    try {
      await lmsService.createLearningEvent({ lesson: practice.lesson, event_type: 'practice_completed' });
      showToast('Practice marked completed.');
    } catch {
      showToast('Login is required to save progress.');
    }
  };

  return (
    <div className="page-shell">
      <ToastMessage message={toast} />
      <Breadcrumbs items={[{ label: practice.lesson_title, active: true }]} />
      <div className="row g-4">
        <div className="col-lg-8">
          <span className="eyebrow">Practice lab</span>
          <h1 className="h2 fw-bold mt-3">{practice.title}</h1>
          <p className="text-muted">{practice.description}</p>
          {practicePdfUrl && (
            <iframe className="w-100 media-frame" style={{ height: 640 }} src={practicePdfUrl} title={practice.title} />
          )}
        </div>
        <aside className="col-lg-4">
          <div className="glass-card position-sticky" style={{ top: 112 }}>
            <div className="card-body">
              <span className="badge premium-badge mb-3">{difficultyLabels[practice.difficulty] || practice.difficulty}</span>
              <div className="resource-row"><span className="text-muted">Taxminiy vaqt</span><strong>{practice.estimated_time} daqiqa</strong></div>
              <p className="text-muted">Barcha biriktirilgan fayllarni bitta ZIP sifatida yuklab olish mumkin.</p>
              <a className="btn btn-brand w-100 mb-3 d-inline-flex align-items-center justify-content-center gap-2" href={`${API_BASE}/practice-materials/${practice.id}/download-all/`}>
                <Download size={17} /> Barchasini yuklab olish
              </a>
              <button className="btn btn-outline-secondary w-100 mb-2 d-inline-flex align-items-center justify-content-center gap-2" type="button" onClick={bookmark}><Bookmark size={17} /> Bookmark</button>
              <button className="btn btn-outline-success w-100 mb-3 d-inline-flex align-items-center justify-content-center gap-2" type="button" onClick={markCompleted}><CheckCircle2 size={17} /> Mark completed</button>
              <div>
                {files.pdf_file && <a className="resource-row text-decoration-none" href={mediaUrl(files.pdf_file)} target="_blank" rel="noreferrer">PDF</a>}
                {files.example_files && <a className="resource-row text-decoration-none" href={mediaUrl(files.example_files)} target="_blank" rel="noreferrer">Example files</a>}
                {files.source_code_files && <a className="resource-row text-decoration-none" href={mediaUrl(files.source_code_files)} target="_blank" rel="noreferrer">Source code files</a>}
              </div>
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}
