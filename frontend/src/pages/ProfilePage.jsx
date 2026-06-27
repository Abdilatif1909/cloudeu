import { useState } from 'react';
import { Lock, Save, User } from 'lucide-react';
import { authService } from '../services/authService.js';
import { useAuth } from '../hooks/useAuth.jsx';

export default function ProfilePage() {
  const { user } = useAuth();
  const [passwords, setPasswords] = useState({ old_password: '', new_password: '' });
  const [message, setMessage] = useState('');

  const changePassword = async (event) => {
    event.preventDefault();
    await authService.changePassword(passwords);
    setMessage('Parol yangilandi.');
    setPasswords({ old_password: '', new_password: '' });
  };

  return (
    <div className="page-shell">
      <section className="hero-panel mb-4">
        <span className="eyebrow"><User size={16} /> Profil</span>
        <h1 className="hero-title">{user.full_name || user.username}</h1>
        <p className="hero-copy">Hisob sozlamalari va xavfsizlik ma'lumotlari.</p>
      </section>
      <div className="row g-4">
        <div className="col-lg-5">
          <div className="glass-card p-4">
            <h2 className="h5 fw-bold">Account</h2>
            <div className="resource-row"><span className="text-muted">Foydalanuvchi</span><strong>{user.username}</strong></div>
            <div className="resource-row"><span className="text-muted">Email</span><strong>{user.email}</strong></div>
            <div className="resource-row"><span className="text-muted">Rol</span><strong>{user.role}</strong></div>
          </div>
        </div>
        <div className="col-lg-7">
          <div className="glass-card p-4">
            <div className="d-flex align-items-center gap-2 mb-3">
              <span className="icon-chip"><Lock size={18} /></span>
              <h2 className="h5 fw-bold mb-0">Parolni almashtirish</h2>
            </div>
            {message && <div className="alert alert-success">{message}</div>}
            <form onSubmit={changePassword}>
              <input className="form-control mb-3" type="password" placeholder="Eski parol" value={passwords.old_password} onChange={(event) => setPasswords({ ...passwords, old_password: event.target.value })} />
              <input className="form-control mb-3" type="password" placeholder="Yangi parol" value={passwords.new_password} onChange={(event) => setPasswords({ ...passwords, new_password: event.target.value })} />
              <button className="btn btn-brand d-inline-flex align-items-center gap-2" type="submit"><Save size={17} /> Saqlash</button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
