import { lazy, Suspense } from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import MainLayout from './layouts/MainLayout.jsx';
import ProtectedRoute from './components/ProtectedRoute.jsx';
import LoadingSkeleton from './components/LoadingSkeleton.jsx';

const CourseListPage = lazy(() => import('./pages/CourseListPage.jsx'));
const CourseDetailPage = lazy(() => import('./pages/CourseDetailPage.jsx'));
const GlossaryPage = lazy(() => import('./pages/GlossaryPage.jsx'));
const LoginPage = lazy(() => import('./pages/LoginPage.jsx'));
const ProfilePage = lazy(() => import('./pages/ProfilePage.jsx'));
const DashboardPage = lazy(() => import('./pages/DashboardPage.jsx'));
const LecturePage = lazy(() => import('./pages/LecturePage.jsx'));
const PracticePage = lazy(() => import('./pages/PracticePage.jsx'));
const ResourcesPage = lazy(() => import('./pages/ResourcesPage.jsx'));
const SearchPage = lazy(() => import('./pages/SearchPage.jsx'));
const VideoPage = lazy(() => import('./pages/VideoPage.jsx'));
const BookmarksPage = lazy(() => import('./pages/BookmarksPage.jsx'));

function PageFallback() {
  return (
    <div className="page-shell">
      <LoadingSkeleton />
    </div>
  );
}

export default function App() {
  return (
    <Suspense fallback={<PageFallback />}>
      <Routes>
        <Route element={<MainLayout />}>
          <Route index element={<Navigate to="/courses" replace />} />
          <Route path="/courses" element={<CourseListPage />} />
          <Route path="/courses/:courseId" element={<CourseDetailPage />} />
          <Route path="/lectures/:lectureId" element={<LecturePage />} />
          <Route path="/practices/:practiceId" element={<PracticePage />} />
          <Route path="/videos/:videoId" element={<VideoPage />} />
          <Route path="/resources" element={<ResourcesPage />} />
          <Route path="/glossary" element={<GlossaryPage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route
            path="/bookmarks"
            element={(
              <ProtectedRoute>
                <BookmarksPage />
              </ProtectedRoute>
            )}
          />
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/dashboard"
            element={(
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            )}
          />
          <Route
            path="/profile"
            element={(
              <ProtectedRoute>
                <ProfilePage />
              </ProtectedRoute>
            )}
          />
        </Route>
      </Routes>
    </Suspense>
  );
}
