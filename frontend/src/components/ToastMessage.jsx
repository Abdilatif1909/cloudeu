import { CheckCircle2, Info } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function ToastMessage({ message, variant = 'success' }) {
  const Icon = variant === 'success' ? CheckCircle2 : Info;
  return (
    <AnimatePresence>
      {message && (
        <motion.div
          className="premium-toast"
          role="alert"
          initial={{ opacity: 0, y: -12, scale: 0.98 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -10, scale: 0.98 }}
        >
          <div className="d-flex align-items-start gap-3">
            <span className="icon-chip"><Icon size={18} /></span>
            <div>
              <div className="fw-bold">{variant === 'success' ? 'Saved' : 'Notice'}</div>
              <div className="small text-muted">{message}</div>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
