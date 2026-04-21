import { Navigate, Route, Routes, useLocation } from 'react-router-dom';
import WorkspacePage from '../pages/WorkspacePage';
import LandingPage from '../pages/LandingPage';
import AiOpsPage from '../pages/AiOpsPage';
import LlmWikiBookPage from '../pages/LlmWikiBookPage';
import PlaybookLibraryPage from '../pages/PlaybookLibraryPage';
import ProjectDetailsPage from '../pages/ProjectDetailsPage';
import { PARTNER_ROUTE_DEFINITIONS } from '../partner/partnerLaneConfig';
import { buildHandoffLocation } from './handoff';
import { readStudioSurfaceState, ROUTES } from './routes';
import { normalizeOpsRoute } from '../ops/app/routes';

function AliasRedirect({ to }: { to: string }) {
  const location = useLocation();

  return (
    <Navigate
      replace
      to={buildHandoffLocation(to, location)}
    />
  );
}

function LegacyAiOpsRedirect({ defaultRoute }: { defaultRoute: string }) {
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search.startsWith('?') ? location.search.slice(1) : location.search);
  searchParams.delete('surface');
  searchParams.set('ops', normalizeOpsRoute(searchParams.get('ops') || defaultRoute));
  const search = searchParams.toString();

  return (
    <Navigate
      replace
      to={{
        pathname: ROUTES.aiOps,
        search: search ? `?${search}` : '',
        hash: location.hash || '',
      }}
    />
  );
}

function StudioEntryRoute() {
  const location = useLocation();
  const { surfaceMode, opsRoute } = readStudioSurfaceState(location.search);

  if (surfaceMode === 'ops') {
    const searchParams = new URLSearchParams(location.search.startsWith('?') ? location.search.slice(1) : location.search);
    searchParams.delete('surface');
    searchParams.set('ops', opsRoute);
    if (opsRoute === 'chat') {
      searchParams.delete('ops');
    }
    const search = searchParams.toString();
    return (
      <Navigate
        replace
        to={{
          pathname: ROUTES.aiOps,
          search: search ? `?${search}` : '',
          hash: location.hash || '',
        }}
      />
    );
  }

  return <WorkspacePage />;
}

export default function AppRoutes() {
  return (
    <Routes>
      <Route path={ROUTES.sharedHome} element={<LandingPage />} />
      <Route path={ROUTES.pbsDetails} element={<ProjectDetailsPage />} />
      <Route path={ROUTES.pbsStudio} element={<StudioEntryRoute />} />
      <Route path={ROUTES.aiOps} element={<AiOpsPage />} />
      <Route path={ROUTES.pbsWikiBook} element={<LlmWikiBookPage />} />
      <Route path={ROUTES.pbsWikiBookAlias} element={<AliasRedirect to={ROUTES.pbsWikiBook} />} />
      <Route path={ROUTES.pbsWorkspaceAlias} element={<StudioEntryRoute />} />
      <Route path={ROUTES.pbsPlaybookLibrary} element={<PlaybookLibraryPage />} />
      <Route path={ROUTES.pbsControlTower} element={<PlaybookLibraryPage />} />
      <Route path={ROUTES.pbsRepository} element={<PlaybookLibraryPage />} />
      {PARTNER_ROUTE_DEFINITIONS.map(({ path, teammatePath }) => (
        <Route
          key={path}
          path={path}
          element={<LegacyAiOpsRedirect defaultRoute={teammatePath.replace(/^\//, '')} />}
        />
      ))}
      <Route path="*" element={<Navigate replace to={ROUTES.sharedHome} />} />
    </Routes>
  );
}
