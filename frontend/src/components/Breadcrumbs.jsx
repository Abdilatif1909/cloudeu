import { Link } from 'react-router-dom';
import { ChevronRight, Home } from 'lucide-react';

export default function Breadcrumbs({ items }) {
  return (
    <nav className="premium-breadcrumb" aria-label="breadcrumb">
      <Link className="d-inline-flex align-items-center gap-1" to="/courses">
        <Home size={15} /> Kurslar
      </Link>
      {items.map((item) => (
        <span className="d-inline-flex align-items-center gap-2" key={item.label}>
          <ChevronRight size={14} />
          {item.to && !item.active ? <Link to={item.to}>{item.label}</Link> : <span className="fw-semibold">{item.label}</span>}
        </span>
      ))}
    </nav>
  );
}
