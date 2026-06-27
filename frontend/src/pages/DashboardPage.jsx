import { useEffect, useState } from 'react';
import { Activity, Award, Bell, BookOpen, Clock3, Flame, GraduationCap, PlayCircle, TrendingUp } from 'lucide-react';
import { lmsService } from '../services/lmsService.js';
import { useAuth } from '../hooks/useAuth.jsx';

export default function DashboardPage() {
  const { user } = useAuth();
  const [summary, setSummary] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    lmsService.progressSummary().then(setSummary);
    lmsService.studentAnalytics().then(setAnalytics).catch(() => setAnalytics(null));
    lmsService.notifications({ ordering: '-created_at' }).then(setNotifications).catch(() => setNotifications([]));
  }, []);

  const weeklyMax = Math.max(...(summary?.weekly_activity || []).map((item) => item.events), 1);

  return (
    <div className="page-shell dashboard-page">
      <section className="hero-panel mb-4">
        <span className="eyebrow"><Activity size={16} /> Student Dashboard</span>
        <div className="d-flex flex-column flex-lg-row justify-content-between gap-4 align-items-lg-end">
          <div>
            <h1 className="hero-title mb-2">{user.full_name || user.username}</h1>
            <p className="hero-copy mb-0">{user.role} · learning analytics, progress, notifications and recent activity.</p>
          </div>
          {summary && (
            <div className="completion-ring" style={{ '--value': `${summary.completion_percentage}%` }}>
              <span>{summary.completion_percentage}%</span>
            </div>
          )}
        </div>
      </section>

      {summary && (
        <>
          <div className="premium-grid mb-4">
            <Metric icon={TrendingUp} title="Overall completion" value={`${summary.completion_percentage}%`} />
            <Metric icon={GraduationCap} title="Completed lessons" value={summary.completed_lessons} />
            <Metric icon={Clock3} title="Study time" value={formatSeconds(summary.total_study_seconds)} />
            <Metric icon={Flame} title="Current streak" value={`${summary.current_streak} days`} />
          </div>
          <div className="row g-4">
            <div className="col-lg-8">
              <section className="glass-card p-4 mb-4">
                <div className="d-flex flex-column flex-md-row justify-content-between gap-3">
                  <div>
                    <span className="eyebrow">Continue learning</span>
                    <h2 className="h4 fw-bold mt-3">{summary.last_visited_lesson?.title || 'Start your next lesson'}</h2>
                    <p className="text-muted mb-0">Resume from your latest activity and keep your study streak moving.</p>
                  </div>
                  <span className="icon-chip align-self-start"><PlayCircle size={20} /></span>
                </div>
              </section>
              <section className="glass-card p-4 mb-4">
                <div className="d-flex justify-content-between align-items-center mb-3">
                  <h2 className="h5 fw-bold mb-0">Weekly activity</h2>
                  <span className="badge premium-badge">Live analytics</span>
                </div>
                <div className="weekly-chart">
                  {summary.weekly_activity.map((item) => (
                    <div className="weekly-bar" key={item.date}>
                      <div className="weekly-bar-fill" style={{ height: `${Math.max((item.events / weeklyMax) * 100, item.events ? 12 : 4)}%` }} />
                      <span>{new Date(item.date).toLocaleDateString(undefined, { weekday: 'short' })}</span>
                    </div>
                  ))}
                </div>
              </section>
              <section className="glass-card p-4 mb-4">
                <div className="d-flex justify-content-between align-items-center mb-3">
                  <h2 className="h5 fw-bold mb-0">Learning heatmap</h2>
                  <span className="small text-muted">14 day pulse</span>
                </div>
                <div className="heatmap">
                  {Array.from({ length: 56 }).map((_, index) => (
                    <span className="heat-cell" data-level={index % 7 === 0 ? 3 : index % 4 === 0 ? 2 : index % 3 === 0 ? 1 : 0} key={index} />
                  ))}
                </div>
              </section>
              <section className="glass-card p-4">
                <h2 className="h5 fw-bold">Learning analytics</h2>
                <div className="premium-grid mt-3">
                  <Metric icon={Clock3} title="Today" value={formatSeconds(analytics?.daily_learning_time || 0)} />
                  <Metric icon={Activity} title="This week" value={formatSeconds(analytics?.weekly_learning_time || 0)} />
                  <Metric icon={TrendingUp} title="Quiz average" value={`${analytics?.average_quiz_score || 0}%`} />
                </div>
              </section>
            </div>
            <div className="col-lg-4">
              <InfoPanel title="Achievements" icon={Award} items={[
                { id: 'streak', title: `${summary.current_streak} day streak` },
                { id: 'completion', title: `${summary.completion_percentage}% course completion` },
                { id: 'quiz', title: `${summary.average_score}% quiz average` },
              ]} />
              <TimelinePanel summary={summary} />
              <InfoPanel title="Last visited lesson" items={summary.last_visited_lesson ? [summary.last_visited_lesson] : []} />
              <InfoPanel title="Notifications" icon={Bell} items={notifications.slice(0, 5)} />
              <InfoPanel title="Recently watched videos" items={summary.recently_watched_videos} metaKey="percentage" suffix="%" />
              <InfoPanel title="Recently downloaded PDFs" items={summary.recently_downloaded_pdfs} />
            </div>
          </div>
        </>
      )}
    </div>
  );
}

function TimelinePanel({ summary }) {
  const items = [
    { title: 'Study session', meta: formatSeconds(summary.total_study_seconds), icon: Clock3 },
    { title: 'Lessons completed', meta: summary.completed_lessons, icon: BookOpen },
    { title: 'Quiz performance', meta: `${summary.average_score}%`, icon: TrendingUp },
  ];
  return (
    <section className="glass-card p-4 mb-3">
      <h2 className="h6 fw-bold mb-3">Activity timeline</h2>
      <div className="timeline">
        {items.map(({ title, meta, icon: Icon }) => (
          <div className="timeline-item" key={title}>
            <span className="icon-chip"><Icon size={17} /></span>
            <div>
              <div className="fw-semibold">{title}</div>
              <div className="small text-muted">{meta}</div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function Metric({ title, value, icon: Icon }) {
  return (
    <div className="stat-card">
      <div className="d-flex justify-content-between gap-3">
        <div>
          <div className="small text-muted">{title}</div>
          <div className="stat-value">{value}</div>
        </div>
        <span className="icon-chip"><Icon size={20} /></span>
      </div>
    </div>
  );
}

function InfoPanel({ title, items = [], metaKey, suffix = '', icon: Icon = Activity }) {
  return (
    <section className="glass-card p-4 mb-3">
      <div className="d-flex align-items-center gap-2 mb-3">
        <span className="icon-chip"><Icon size={18} /></span>
        <h2 className="h6 fw-bold mb-0">{title}</h2>
      </div>
      {items.length ? items.map((item, index) => (
        <div className="resource-row" key={`${title}-${item.id || index}`}>
          <span className="fw-semibold">{item.title || 'Untitled'}</span>
          {metaKey && <span className="badge premium-badge">{item[metaKey]}{suffix}</span>}
        </div>
      )) : <div className="text-muted small">No data yet.</div>}
    </section>
  );
}

function formatSeconds(seconds) {
  const minutes = Math.round((seconds || 0) / 60);
  if (minutes < 60) return `${minutes} min`;
  return `${Math.floor(minutes / 60)}h ${minutes % 60}m`;
}
