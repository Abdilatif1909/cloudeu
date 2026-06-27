import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { LogIn } from 'lucide-react';
import { useAuth } from '../hooks/useAuth.jsx';

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: '', password: '' });
  const [error, setError] = useState('');

  const submit = async (event) => {
    event.preventDefault();
    setError('');
    try {
      await login(form.username, form.password);
      navigate('/dashboard');
    } catch {
      setError('Login yoki parol noto\'g\'ri.');
    }
  };

  return (
    <div className="page-shell">
      <div className="row justify-content-center align-items-center" style={{ minHeight: '68vh' }}>
        <div className="col-lg-5">
          <div className="glass-card p-4 p-md-5">
            <img className="brand-logo brand-logo-login mb-4" src="/static/frontend/brand-logo.svg" alt="Axborot Texnologiyalari va Menejment Universiteti" />
            <span className="eyebrow">Secure access</span>
            <h1 className="h2 fw-bold mt-3 mb-2">Cloud Education Platform</h1>
            <p className="text-muted">cloude.uz orqali Sun'iy intellekt asoslari kursiga kiring.</p>
            {error && <div className="alert alert-danger">{error}</div>}
            <form onSubmit={submit}>
              <label className="form-label fw-semibold">Username</label>
              <input className="form-control mb-3" value={form.username} onChange={(event) => setForm({ ...form, username: event.target.value })} />
              <label className="form-label fw-semibold">Parol</label>
              <input className="form-control mb-4" type="password" value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} />
              <button className="btn btn-brand w-100 d-inline-flex align-items-center justify-content-center gap-2" type="submit"><LogIn size={18} /> Kirish</button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
