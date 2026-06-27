import { useEffect, useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Award, BookOpen, CheckCircle2, Download, FileText, GraduationCap, PlayCircle, TestTube2, UserRound } from 'lucide-react';
import { motion } from 'framer-motion';
import ToastMessage from '../components/ToastMessage.jsx';
import { lmsService } from '../services/lmsService.js';

const resourceMeta = {
  lectures: { title: "Ma'ruza PDF", icon: FileText, toPrefix: '/lectures' },
  practices: { title: "Amaliy mashg'ulotlar", icon: CheckCircle2, toPrefix: '/practices' },
  videos: { title: 'Videolar', icon: PlayCircle, toPrefix: '/videos' },
  resources: { title: 'Resurslar', icon: Download, fileKey: 'file' },
  quizzes: { title: 'Testlar', icon: TestTube2 },
};

export default function CourseDetailPage() {
  const { courseId } = useParams();
  const [course, setCourse] = useState(null);
  const [lessons, setLessons] = useState([]);
  const [lectures, setLectures] = useState([]);
  const [practices, setPractices] = useState([]);
  const [videos, setVideos] = useState([]);
  const [quizzes, setQuizzes] = useState([]);
  const [resources, setResources] = useState([]);
  const [toast, setToast] = useState('');

  useEffect(() => {
    lmsService.course(courseId).then(setCourse);
    lmsService.lessons({ course: courseId, ordering: 'order' }).then(setLessons);
    lmsService.lectures({ lesson__course: courseId }).then(setLectures);
    lmsService.practices({ lesson__course: courseId }).then(setPractices);
    lmsService.videos({ lesson__course: courseId }).then(setVideos);
    lmsService.quizzes({ lesson__course: courseId }).then(setQuizzes);
    lmsService.resources({ course: courseId }).then(setResources);
  }, [courseId]);

  const resourcesByLesson = useMemo(() => {
    const bucket = {};
    lessons.forEach((lesson) => {
      bucket[lesson.id] = { lectures: [], practices: [], videos: [], quizzes: [], resources: [] };
      (lesson.lecture_materials || []).forEach((item) => bucket[lesson.id].lectures.push(item));
      (lesson.practice_materials || []).forEach((item) => bucket[lesson.id].practices.push(item));
      (lesson.videos || []).forEach((item) => bucket[lesson.id].videos.push(item));
      (lesson.quizzes || []).forEach((item) => bucket[lesson.id].quizzes.push(item));
      (lesson.resources || []).forEach((item) => bucket[lesson.id].resources.push(item));
    });
    const appendUnique = (lessonId, key, item) => {
      const target = bucket[lessonId]?.[key];
      if (target && !target.some((existing) => existing.id === item.id)) {
        target.push(item);
      }
    };
    lectures.forEach((item) => appendUnique(item.lesson, 'lectures', item));
    practices.forEach((item) => appendUnique(item.lesson, 'practices', item));
    videos.forEach((item) => appendUnique(item.lesson, 'videos', item));
    quizzes.forEach((item) => appendUnique(item.lesson, 'quizzes', item));
    resources.forEach((item) => item.lesson && appendUnique(item.lesson, 'resources', item));
    return bucket;
  }, [lessons, lectures, practices, videos, quizzes, resources]);

  const contentTotals = useMemo(() => Object.values(resourcesByLesson).reduce((totals, lessonResources) => ({
    lectures: totals.lectures + lessonResources.lectures.length,
    practices: totals.practices + lessonResources.practices.length,
    videos: totals.videos + lessonResources.videos.length,
    quizzes: totals.quizzes + lessonResources.quizzes.length,
  }), { lectures: 0, practices: 0, videos: 0, quizzes: 0 }), [resourcesByLesson]);

  if (!course) return <div className="page-shell"><div className="glass-card p-4">Yuklanmoqda...</div></div>;

  const issueCertificate = async () => {
    try {
      const certificate = await lmsService.issueCertificate(course.id);
      setToast(`Certificate issued: ${certificate.certificate_id}`);
    } catch {
      setToast('Certificate requires 100% lesson completion and quiz average >=70%.');
    }
    setTimeout(() => setToast(''), 3000);
  };

  return (
    <div className="page-shell">
      <ToastMessage message={toast} />
      <section className="hero-panel mb-4">
        <span className="eyebrow"><BookOpen size={16} /> {course.code}</span>
        <h1 className="hero-title">{course.title}</h1>
        <p className="hero-copy">{course.description}</p>
        <button className="btn btn-brand btn-lg d-inline-flex align-items-center gap-2 mt-3" type="button" onClick={issueCertificate}>
          <Award size={19} /> Generate certificate
        </button>
        <div className="floating-card">
          <div className="d-flex align-items-center gap-3">
            <span className="icon-chip"><GraduationCap size={19} /></span>
            <div>
              <div className="fw-bold">{lessons.length} lesson learning path</div>
              <div className="small text-muted">{course.credits} credits · {course.semester}-semester</div>
            </div>
          </div>
        </div>
      </section>

      <div className="row g-4">
        <div className="col-lg-8">
          <div className="d-flex align-items-end justify-content-between gap-3 mb-3">
            <div>
              <span className="eyebrow">Learning path</span>
              <h2 className="h3 mt-3 mb-0 fw-bold">Darslar</h2>
            </div>
            <span className="text-muted small">{lessons.length} modules</span>
          </div>
          <div className="timeline">
            {lessons.map((lesson, index) => (
              <motion.article className="glass-card p-3 p-md-4" key={lesson.id} initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.035 }}>
                <div className="timeline-item">
                  <span className="icon-chip fw-bold">{lesson.lesson_number}</span>
                  <div className="flex-grow-1">
                    <h3 className="h5 fw-bold mb-1">{lesson.title}</h3>
                    <p className="text-muted mb-3">{lesson.description}</p>
                    {Object.entries(resourceMeta).map(([key, meta]) => (
                      <ResourceList key={key} items={resourcesByLesson[lesson.id]?.[key]} {...meta} />
                    ))}
                  </div>
                </div>
              </motion.article>
            ))}
          </div>
        </div>
        <aside className="col-lg-4">
          <div className="glass-card p-4 position-sticky" style={{ top: 112 }}>
            <h2 className="h5 fw-bold">Course overview</h2>
            <div className="d-flex gap-3 align-items-center my-3 p-3 rounded-4" style={{ background: 'rgba(79, 70, 229, 0.08)' }}>
              <span className="icon-chip"><UserRound size={18} /></span>
              <div>
                <div className="fw-bold">AI Faculty</div>
                <div className="small text-muted">Instructor-led digital learning</div>
              </div>
            </div>
            <div className="resource-row">
              <span className="text-muted">Ma'ruzalar</span>
              <strong>{contentTotals.lectures}</strong>
            </div>
            <div className="resource-row">
              <span className="text-muted">Amaliyotlar</span>
              <strong>{contentTotals.practices}</strong>
            </div>
            <div className="resource-row">
              <span className="text-muted">Videolar</span>
              <strong>{contentTotals.videos}</strong>
            </div>
            <div className="resource-row">
              <span className="text-muted">Testlar</span>
              <strong>{contentTotals.quizzes}</strong>
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}

function ResourceList({ title, items = [], fileKey, toPrefix, icon: Icon }) {
  if (!items.length) return null;
  return (
    <div className="mb-2">
      <div className="small fw-bold text-muted mb-1">{title}</div>
      {items.map((item) => {
        const label = item.title || item.description || item[fileKey] || 'Untitled';
        const content = (
          <>
            <span className="d-flex align-items-center gap-2"><Icon size={17} /> {label}</span>
            <span className="badge premium-badge">Open</span>
          </>
        );
        if (toPrefix) {
          return <Link className="resource-row text-decoration-none" to={`${toPrefix}/${item.id}`} key={item.id}>{content}</Link>;
        }
        if (!fileKey) {
          return <div className="resource-row" key={item.id}>{content}</div>;
        }
        return <a className="resource-row text-decoration-none" href={item[fileKey]} target="_blank" rel="noreferrer" key={item.id}>{content}</a>;
      })}
    </div>
  );
}
