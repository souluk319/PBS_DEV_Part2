import { useMemo } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ArrowRight, Sparkles } from 'lucide-react';
import { buildAiOpsHref, readAiOpsRouteState, ROUTES } from '../app/routes';
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
      <header className="aiops-page__header">
        <div className="aiops-page__brand">
          <div className="aiops-page__brand-icon">
            <Sparkles size={16} />
          </div>
          <div className="aiops-page__brand-copy">
            <span className="aiops-page__eyebrow">OCP OPS</span>
            <strong>AI Ops</strong>
          </div>
        </div>
        <nav className="aiops-page__nav" aria-label="AI Ops quick navigation">
          <Link to={ROUTES.sharedHome} className="aiops-page__nav-link">
            <span>Landing</span>
          </Link>
          <Link to={ROUTES.pbsStudio} className="aiops-page__nav-link">
            <span>Studio</span>
          </Link>
          <Link to={buildAiOpsHref(opsRoute)} className="aiops-page__nav-link is-active" aria-current="page">
            <span>AI Ops</span>
            <ArrowRight size={14} />
          </Link>
        </nav>
      </header>
      <iframe
        key={iframeSrc}
        className="aiops-page__frame"
        src={iframeSrc}
        title="AI Ops"
      />
    </div>
  );
}
