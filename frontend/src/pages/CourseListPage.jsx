import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, BookOpen, CheckCircle2, Clock3, GraduationCap, Layers3, Search, Sparkles, Trophy } from 'lucide-react';
import { motion } from 'framer-motion';
import { lmsService } from '../services/lmsService.js';

const BRAND_LOGO = `${import.meta.env.BASE_URL}brand-logo.svg`;

export default function CourseListPage() {
  const [courses, setCourses] = useState([]);
  const [search, setSearch] = useState('');

  useEffect(() => {
    lmsService.courses({ search }).then(setCourses);
  }, [search]);

  const totalCredits = courses.reduce((sum, course) => sum + (Number(course.credits) || 0), 0);

  return (
    <div className="page-shell">
      <motion.section className="hero-panel mb-4" initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }}>
        <img className="brand-logo brand-logo-hero mb-3" src={BRAND_LOGO} alt="Axborot Texnologiyalari va Menejment Universiteti logo" />
        <span className="eyebrow"><Sparkles size={16} /> Cloud Education Platform</span>
        <h1 className="hero-title">Sun'iy intellekt asoslari</h1>
        <p className="hero-copy">Axborot Texnologiyalari va Menejment Universiteti uchun cloude.uz platformasida ma'ruzalar, amaliy materiallar, videolar, testlar va progress nazorati jamlangan.</p>
        <div className="d-flex flex-wrap gap-3 mt-4">
          <Link className="btn btn-brand btn-lg d-inline-flex align-items-center gap-2" to={courses[0] ? `/courses/${courses[0].id}` : '/courses'}>
            Boshlash <ArrowRight size={18} />
          </Link>
          <Link className="btn btn-outline-secondary btn-lg" to="/resources">Materiallar</Link>
        </div>
        <div className="floating-card">
          <div className="d-flex align-items-center gap-3 mb-3">
            <span className="icon-chip"><Layers3 size={19} /></span>
            <div>
              <div className="fw-bold">Cloud Education Platform</div>
              <div className="small text-muted">cloude.uz learning workspace</div>
            </div>
          </div>
          <div className="d-flex align-items-end gap-2" style={{ height: 92 }}>
            {[48, 72, 54, 88, 66, 96, 78, 86].map((height, index) => (
              <span className="weekly-bar-fill flex-fill" style={{ height: `${height}%` }} key={index} />
            ))}
          </div>
        </div>
      </motion.section>

      <div className="premium-grid mb-4">
        <Stat icon={GraduationCap} value={courses.length} label="Aktiv kurslar" />
        <Stat icon={BookOpen} value="11+" label="Modulli kontent" />
        <Stat icon={Trophy} value={totalCredits || 5} label="Kredit yuklamasi" />
        <Stat icon={Clock3} value="24/7" label="O'qish imkoniyati" />
      </div>

      <div className="row g-4 mb-4">
        <div className="col-lg-7">
          <section className="glass-card p-4 h-100">
            <span className="eyebrow">Learning roadmap</span>
            <h2 className="h3 fw-bold mt-3">AI bilimlarini bosqichma-bosqich egallang</h2>
            <div className="roadmap mt-4">
              {[
                ['Foundations', 'AI tushunchalari, muammo shakllantirish va agentlar.'],
                ['Data workflow', "NumPy, Pandas va vizual tahlil orqali ma'lumot bilan ishlash."],
                ['Model building', 'Machine learning, neural networks, CNN, NLP va reinforcement learning.'],
              ].map(([title, copy]) => (
                <div className="roadmap-item" key={title}>
                  <span className="icon-chip"><CheckCircle2 size={18} /></span>
                  <div>
                    <div className="fw-bold">{title}</div>
                    <div className="text-muted small">{copy}</div>
                  </div>
                </div>
              ))}
            </div>
          </section>
        </div>
        <div className="col-lg-5">
          <section className="glass-card p-4 h-100">
            <span className="eyebrow">Course preview</span>
            <h2 className="h4 fw-bold mt-3">Cloud Education Platform</h2>
            <p className="text-muted">PDF reader, video lessons, resources, glossary, bookmarks, analytics and certificates work together as a single university learning product.</p>
            <div className="d-grid gap-2">
              {['Magazine-quality lecture reader', 'Netflix-style video lessons', 'Spotlight search across content'].map((item) => (
                <div className="resource-row" key={item}>
                  <span>{item}</span>
                  <span className="badge premium-badge">Ready</span>
                </div>
              ))}
            </div>
          </section>
        </div>
      </div>

      <section className="glass-card p-3 p-md-4">
        <div className="d-flex flex-column flex-lg-row justify-content-between gap-3 mb-4">
          <div>
            <span className="eyebrow">Course catalog</span>
            <h2 className="h3 mt-3 mb-1 fw-bold">Kurslar</h2>
            <p className="text-muted mb-0">Fanlar premium dashboard tajribasi uchun tuzilgan.</p>
          </div>
          <label className="position-relative" style={{ minWidth: 280 }}>
            <Search className="position-absolute top-50 translate-middle-y ms-3 text-muted" size={18} />
            <input
              className="form-control ps-5"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Kurs qidirish"
              aria-label="Kurs qidirish"
            />
          </label>
        </div>
        <div className="row g-3">
          {courses.map((course, index) => (
            <motion.div className="col-md-6 col-xl-4" key={course.id} initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.04 }}>
              <div className="card h-100">
                {course.image && <img className="card-img-top" src={course.image} alt={course.title} />}
                <div className="card-body d-flex flex-column">
                  <span className="badge premium-badge align-self-start mb-3">{course.code}</span>
                  <h3 className="h5 fw-bold">{course.title}</h3>
                  <p className="text-muted flex-grow-1">{course.description}</p>
                  <div className="d-flex justify-content-between small text-muted mb-3">
                    <span>{course.semester}-semestr</span>
                    <span>{course.credits} kredit</span>
                  </div>
                  <Link className="btn btn-brand d-inline-flex align-items-center justify-content-center gap-2" to={`/courses/${course.id}`}>
                    Kursni ochish <ArrowRight size={17} />
                  </Link>
                </div>
              </div>
            </motion.div>
          ))}
          {!courses.length && (
            <div className="col-12">
              <div className="empty-state">
                <div>
                  <span className="brand-mark mx-auto mb-3"><Search size={22} /></span>
                  <h3 className="h5 fw-bold">No courses found</h3>
                  <p className="text-muted mb-0">Try a different keyword or clear the search field.</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}

function Stat({ icon: Icon, value, label }) {
  return (
    <div className="stat-card">
      <div className="d-flex align-items-center justify-content-between">
        <div>
          <div className="stat-value">{value}</div>
          <div className="text-muted">{label}</div>
        </div>
        <span className="icon-chip"><Icon size={20} /></span>
      </div>
    </div>
  );
}
