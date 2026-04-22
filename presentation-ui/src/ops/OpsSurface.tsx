import { useMemo } from 'react';
import { App as OpsApp } from './app/App';
import type { OpsRoute } from './app/routes';
import type { HandoffPayload } from '../app/handoff';
import './styles/ops.css';

type OpsSurfaceProps = {
  route: OpsRoute;
  onNavigate: (route: OpsRoute) => void;
  handoff?: HandoffPayload | null;
  onDismissHandoff?: () => void;
  onReturnToPlaybook?: (context?: { sourceSessionId?: string; intentSummary?: string; sourceRoute?: string }) => void;
};

const DEFAULT_OPS_API_BASE_URL = 'http://127.0.0.1:8000';

export default function OpsSurface({
  route,
  onNavigate,
  handoff,
  onDismissHandoff,
  onReturnToPlaybook,
}: OpsSurfaceProps) {
  const apiBaseUrl = useMemo(
    () => import.meta.env.VITE_OPS_API_BASE_URL ?? DEFAULT_OPS_API_BASE_URL,
    [],
  );

  return (
    <div className="ops-surface">
      <OpsApp
        route={route}
        onNavigate={onNavigate}
        apiBaseUrl={apiBaseUrl}
        handoff={handoff}
        onDismissHandoff={onDismissHandoff}
        onReturnToPlaybook={onReturnToPlaybook}
      />
    </div>
  );
}
