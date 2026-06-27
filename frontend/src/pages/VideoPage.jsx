import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Bookmark, CheckCircle2, Save } from 'lucide-react';
import Breadcrumbs from '../components/Breadcrumbs.jsx';
import ToastMessage from '../components/ToastMessage.jsx';
import { lmsService } from '../services/lmsService.js';

export default function VideoPage() {
  const { videoId } = useParams();
  const [video, setVideo] = useState(null);
  const [related, setRelated] = useState([]);
  const [nav, setNav] = useState({});
  const [progress, setProgress] = useState(null);
  const [position, setPosition] = useState(0);
  const [notes, setNotes] = useState('');
  const [toast, setToast] = useState('');

  useEffect(() => {
    lmsService.video(videoId).then(setVideo);
    lmsService.videoRelated(videoId).then(setRelated);
    lmsService.videoNavigation(videoId).then(setNav);
    lmsService.videoWatchProgress(videoId).then((data) => {
      setProgress(data);
      setPosition(data.current_position || 0);
    }).catch(() => {});
  }, [videoId]);

  const markComplete = async () => {
    const saved = await lmsService.updateWatchProgress(videoId, { watched_seconds: position, current_position: position, completed: true });
    setProgress(saved);
    setToast('Video progress saqlandi.');
    setTimeout(() => setToast(''), 2500);
  };

  const savePosition = async () => {
    const saved = await lmsService.updateWatchProgress(videoId, { watched_seconds: position, current_position: position });
    setProgress(saved);
    setToast('Playback position saved.');
    setTimeout(() => setToast(''), 2500);
  };

  const bookmark = async () => {
    try {
      await lmsService.createBookmark({ target_type: 'video', object_id: video.id, title: video.title, url: `/videos/${video.id}` });
      setToast('Video bookmarked.');
    } catch {
      setToast('Bookmark already exists or login is required.');
    }
    setTimeout(() => setToast(''), 2500);
  };

  if (!video) return <div className="page-shell"><div className="glass-card p-4">Yuklanmoqda...</div></div>;

  return (
    <div className="page-shell">
      <ToastMessage message={toast} />
      <Breadcrumbs items={[{ label: video.title, active: true }]} />
      <div className="row g-4">
        <div className="col-lg-8">
          <div className="ratio ratio-16x9 mb-4 media-frame">
            <iframe src={`https://www.youtube.com/embed/${video.video_id}?start=${position || 0}`} title={video.title} allowFullScreen />
          </div>
          <span className="eyebrow">Video lesson</span>
          <h1 className="h2 fw-bold mt-3">{video.title}</h1>
          <p className="text-muted">{video.speaker}</p>
          <p>{video.description}</p>
          {progress && (
            <div className="progress mb-3" style={{ height: 8 }}>
              <div className="progress-bar" style={{ width: `${progress.watch_percentage || 0}%` }} />
            </div>
          )}
          <div className="glass-card p-3 d-flex flex-wrap gap-2 align-items-center">
            <input className="form-control" style={{ maxWidth: 180 }} type="number" min="0" value={position} onChange={(event) => setPosition(Number(event.target.value))} />
            <button className="btn btn-outline-secondary d-inline-flex align-items-center gap-2" type="button" onClick={savePosition}><Save size={17} /> Save position</button>
            <button className="btn btn-brand d-inline-flex align-items-center gap-2" type="button" onClick={markComplete}><CheckCircle2 size={17} /> Ko'rildi deb belgilash</button>
            <button className="btn btn-outline-secondary d-inline-flex align-items-center gap-2" type="button" onClick={bookmark}><Bookmark size={17} /> Bookmark</button>
          </div>
        </div>
        <aside className="col-lg-4">
          <div className="d-flex gap-2 mb-3">
            {nav.previous && <Link className="btn btn-outline-secondary flex-fill" to={`/videos/${nav.previous.id}`}>Oldingi</Link>}
            {nav.next && <Link className="btn btn-outline-secondary flex-fill" to={`/videos/${nav.next.id}`}>Keyingi</Link>}
          </div>
          <div className="glass-card p-4 mb-3">
            <h2 className="h5 fw-bold">Video chapters</h2>
            {['Introduction', 'Core concepts', 'Examples', 'Summary'].map((chapter, index) => (
              <button className="resource-row border-0 bg-transparent w-100 text-start" type="button" onClick={() => setPosition(index * 180)} key={chapter}>
                <span>{chapter}</span>
                <span className="badge premium-badge">{index * 3}:00</span>
              </button>
            ))}
          </div>
          <div className="glass-card p-4 mb-3">
            <h2 className="h5 fw-bold">Lesson notes</h2>
            <textarea className="form-control" rows="7" value={notes} onChange={(event) => setNotes(event.target.value)} placeholder="Capture ideas while watching..." />
          </div>
          <div className="glass-card p-4">
          <h2 className="h5 fw-bold">Bog'liq videolar</h2>
            {related.map((item) => (
              <Link className="resource-row text-decoration-none" to={`/videos/${item.id}`} key={item.id}>
                {item.title}
              </Link>
            ))}
          </div>
        </aside>
      </div>
    </div>
  );
}
