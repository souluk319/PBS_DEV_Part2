import { useMemo } from 'react';
import { useLocation } from 'react-router-dom';
import { readAiOpsRouteState } from '../app/routes';
import './AiOpsPage.css';

const DEFAULT_AIOPS_UI_URL = 'http://127.0.0.1:5174';

function buildAiOpsInnerPath(route: ReturnType<typeof readAiOpsRouteState>['opsRoute']): string {
  switch (route) {
    case 'overview':
      return '/overview';
    case 'resources':
      return '/resources';
    case 'library':
      return '/library';
    case 'actions':
      return '/actions';
    case 'connections':
      return '/connections';
    case 'models':
      return '/models';
    case 'scm':
      return '/scm';
    case 'chat':
    default:
      return '/chat';
  }
}

export default function AiOpsPage() {
  const location = useLocation();
  const { opsRoute } = useMemo(
    () => readAiOpsRouteState(location.search),
    [location.search],
  );

  const iframeSrc = useMemo(() => {
    const baseUrl = (import.meta.env.VITE_AIOPS_UI_BASE_URL ?? DEFAULT_AIOPS_UI_URL).replace(/\/$/, '');
    return `${baseUrl}${buildAiOpsInnerPath(opsRoute)}`;
  }, [opsRoute]);

  return (
    <div className="aiops-page">
      <iframe
        key={iframeSrc}
        className="aiops-page__frame"
        src={iframeSrc}
        title="AI Ops"
      />
    </div>
  );
}
