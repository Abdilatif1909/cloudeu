export default function LoadingSkeleton({ rows = 4 }) {
  return (
    <div className="glass-card p-4">
      <div className="skeleton-line mb-4" style={{ width: '44%', height: 28 }} />
      {Array.from({ length: rows }).map((_, index) => (
        <div className="skeleton-line mb-3" style={{ width: `${92 - index * 8}%` }} key={index} />
      ))}
      <div className="premium-grid mt-4">
        <div className="skeleton-line" style={{ height: 110 }} />
        <div className="skeleton-line" style={{ height: 110 }} />
        <div className="skeleton-line" style={{ height: 110 }} />
      </div>
    </div>
  );
}
