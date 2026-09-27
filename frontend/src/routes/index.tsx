import { createBrowserRouter, Navigate } from 'react-router-dom';
import { MainLayout } from '../layouts/MainLayout';
import { DashboardPage } from '../pages/DashboardPage';
import { RecommendationPage } from '../pages/RecommendationPage';
import { CatalogPage } from '../pages/CatalogPage';
import { ArchitecturePage } from '../pages/ArchitecturePage';
import { HistoryPage } from '../pages/HistoryPage';
import { SystemStatusPage } from '../pages/SystemStatusPage';
import { NotFoundPage } from '../pages/NotFoundPage';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <MainLayout />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: 'recommend', element: <RecommendationPage /> },
      { path: 'materials', element: <CatalogPage /> },
      { path: 'catalog', element: <Navigate to="/materials" replace /> },
      { path: 'history', element: <HistoryPage /> },
      { path: 'architecture', element: <ArchitecturePage /> },
      { path: 'status', element: <SystemStatusPage /> },
      { path: '404', element: <NotFoundPage /> },
      { path: '*', element: <Navigate to="/404" replace /> },
    ],
  },
]);
