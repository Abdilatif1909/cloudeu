import { useEffect, useState } from 'react';
import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom';
import {
  Bell,
  BookOpen,
  Bookmark,
  ChevronsLeft,
  ChevronsRight,
  GraduationCap,
  LayoutDashboard,
  Library,
  LogIn,
  LogOut,
  Moon,
  Search,
  Sun,
} from 'lucide-react';
import SpotlightSearch from '../components/SpotlightSearch.jsx';
import { useAuth } from '../hooks/useAuth.jsx';

const navItems = [
  { to: '/courses', label: 'Kurslar', icon: GraduationCap },
  { to: '/resources', label: 'Resurslar', icon: Library },
  { to: '/glossary', label: 'Glossariy', icon: BookOpen },
  { to: '/search', label: 'Qidiruv', icon: Search },
];

export default function MainLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [darkMode, setDarkMode] = useState(() => localStorage.getItem('darkMode') === 'true');
  const [collapsed, setCollapsed] = useState(() => localStorage.getItem('sidebarCollapsed') === 'true');
  const [spotlightOpen, setSpotlightOpen] = useState(false);

  useEffect(() => {
    document.body.classList.toggle('dark-mode', darkMode);
    localStorage.setItem('darkMode', String(darkMode));
  }, [darkMode]);

  useEffect(() => {
    localStorage.setItem('sidebarCollapsed', String(collapsed));
  }, [collapsed]);

  useEffect(() => {
    const openSearch = (event) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault();
        setSpotlightOpen(true);
      }
    };
    window.addEventListener('keydown', openSearch);
    return () => window.removeEventListener('keydown', openSearch);
  }, []);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const allNavItems = user
    ? [...navItems, { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard }, { to: '/bookmarks', label: 'Bookmarks', icon: Bookmark }]
    : navItems;

  return (
    <div className={`app-frame ${collapsed ? 'sidebar-collapsed' : ''}`}>
      <SpotlightSearch open={spotlightOpen} onClose={() => setSpotlightOpen(false)} />
      <aside className="app-sidebar">
        <Link className="d-flex align-items-center gap-3 mb-4 text-decoration-none" to="/courses" aria-label="Cloud Education Platform home">
          <img
            src="/static/frontend/brand-logo.svg"
            alt="Axborot Texnologiyalari va Menejment Universiteti"
            className="site-logo"
          />
          <span className="brand-copy">
            <span className="d-block fw-bold fs-5">cloude.uz</span>
            <span className="d-block small text-muted sidebar-meta">Cloud Education Platform</span>
          </span>
        </Link>
        <nav className="sidebar-nav" aria-label="Primary navigation">
          {allNavItems.map(({ to, label, icon: Icon }) => (
            <NavLink className="nav-pill" to={to} key={to}>
              <Icon size={18} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-bottom position-absolute start-0 end-0 bottom-0 p-3">
          <div className="glass-card p-3">
            <div className="small fw-bold">Learning velocity</div>
            <div className="d-flex align-items-end gap-1 mt-3" style={{ height: 48 }}>
              {[36, 58, 42, 72, 64, 86, 76].map((height, index) => (
                <span className="weekly-bar-fill flex-fill" style={{ height: `${height}%` }} key={index} />
              ))}
            </div>
          </div>
        </div>
      </aside>
      <div className="app-main">
        <header className="topbar">
          <div className="d-flex align-items-center gap-2">
            <button className="btn btn-outline-secondary btn-sm" type="button" onClick={() => setCollapsed((value) => !value)} aria-label="Toggle sidebar">
              {collapsed ? <ChevronsRight size={17} /> : <ChevronsLeft size={17} />}
            </button>
            <img
              src="/static/frontend/brand-logo.svg"
              alt="Axborot Texnologiyalari va Menejment Universiteti"
              className="site-logo"
            />
            <button className="topbar-search border-0 text-start" type="button" onClick={() => setSpotlightOpen(true)}>
              <Search size={18} />
              <span>Search anything...</span>
              <span className="kbd">Ctrl K</span>
            </button>
          </div>
          <div className="d-flex align-items-center gap-2 flex-wrap">
            <button className="btn btn-outline-secondary btn-sm position-relative" type="button" aria-label="Notifications">
              <Bell size={16} />
              <span className="position-absolute top-0 start-100 translate-middle p-1 bg-danger border border-light rounded-circle" />
            </button>
            <button
              className="btn btn-outline-secondary btn-sm d-inline-flex align-items-center gap-2"
              type="button"
              onClick={() => setDarkMode((value) => !value)}
              aria-label="Toggle theme"
            >
              {darkMode ? <Sun size={16} /> : <Moon size={16} />}
              {darkMode ? 'Light' : 'Dark'}
            </button>
            {user ? (
              <>
                <Link className="avatar-button text-decoration-none" to="/profile" aria-label="Profile">
                  {(user.full_name || user.username || 'U').slice(0, 1).toUpperCase()}
                </Link>
                <button className="btn btn-brand btn-sm d-inline-flex align-items-center gap-2" type="button" onClick={handleLogout}>
                  <LogOut size={16} />
                  Chiqish
                </button>
              </>
            ) : (
              <Link className="btn btn-brand btn-sm d-inline-flex align-items-center gap-2" to="/login">
                <LogIn size={16} />
                Kirish
              </Link>
            )}
          </div>
        </header>
        <main className="content-shell">
          <Outlet />
        </main>
        <footer className="footer-line small">
          <p className="fw-bold mb-1">Cloud Education Platform</p>
          <p>Sun'iy intellekt asoslari - Axborot Texnologiyalari va Menejment Universiteti</p>
          <a href="mailto:abdilatif1909@gmail.com">abdilatif1909@gmail.com</a>
          <p>2026 (c) Axborot Texnologiyalari va Menejment Universiteti</p>
        </footer>
      </div>
    </div>
  );
}
