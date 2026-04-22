import {
  DEFAULT_OPS_ROUTE,
  normalizeOpsRoute,
  type OpsRoute,
} from '../ops/app/routes';

export const ROUTES = {
  sharedHome: '/',
  pbsDetails: '/details',
  pbsStudio: '/studio',
  aiOps: '/aiops',
  pbsWorkspaceAlias: '/workspace',
  pbsWikiBook: '/llmwikibook',
  pbsWikiBookAlias: '/studio-v2',
  pbsPlaybookLibrary: '/playbook-library',
  pbsControlTower: '/playbook-library/control-tower',
  pbsRepository: '/playbook-library/repository',
  partnerHome: '/partner',
  partnerWorkspace: '/partner/workspace',
  partnerLibrary: '/partner/library',
  partnerViewer: '/partner/viewer',
  partnerDetails: '/partner/details',
} as const;

export type SharedLandingTab = 'pbs' | 'partner';
export type WorkspaceSurfaceMode = 'pbs' | 'ops';

export const RESERVED_PBS_PATH_PREFIXES = [
  ROUTES.pbsPlaybookLibrary,
  ROUTES.pbsStudio,
  ROUTES.pbsWikiBook,
] as const;

export const PARTNER_NAMESPACE_PATHS = [
  ROUTES.partnerHome,
  ROUTES.partnerWorkspace,
  ROUTES.partnerLibrary,
  ROUTES.partnerViewer,
  ROUTES.partnerDetails,
] as const;

export function normalizeSharedLandingTab(value: string | null | undefined): SharedLandingTab {
  return value === 'partner' ? 'partner' : 'pbs';
}

export function buildSharedLandingHref(_tab: SharedLandingTab = 'pbs'): string {
  return ROUTES.sharedHome;
}

export function normalizeWorkspaceSurfaceMode(value: string | null | undefined): WorkspaceSurfaceMode {
  return value === 'ops' ? 'ops' : 'pbs';
}

export function readStudioSurfaceState(
  searchLike: string | URLSearchParams | null | undefined,
): { surfaceMode: WorkspaceSurfaceMode; opsRoute: OpsRoute } {
  const search =
    typeof searchLike === 'string'
      ? new URLSearchParams(searchLike.startsWith('?') ? searchLike.slice(1) : searchLike)
      : new URLSearchParams(searchLike ?? undefined);
  const surfaceMode = normalizeWorkspaceSurfaceMode(search.get('surface'));
  return {
    surfaceMode,
    opsRoute: normalizeOpsRoute(search.get('ops')),
  };
}

export function buildStudioHref(options?: {
  surfaceMode?: WorkspaceSurfaceMode;
  opsRoute?: OpsRoute;
}): string {
  const surfaceMode = options?.surfaceMode ?? 'pbs';
  if (surfaceMode !== 'ops') {
    return ROUTES.pbsStudio;
  }
  const search = new URLSearchParams({
    surface: 'ops',
    ops: normalizeOpsRoute(options?.opsRoute ?? DEFAULT_OPS_ROUTE),
  });
  return `${ROUTES.pbsStudio}?${search.toString()}`;
}

export function readAiOpsRouteState(
  searchLike: string | URLSearchParams | null | undefined,
): { opsRoute: OpsRoute } {
  const search =
    typeof searchLike === 'string'
      ? new URLSearchParams(searchLike.startsWith('?') ? searchLike.slice(1) : searchLike)
      : new URLSearchParams(searchLike ?? undefined);
  return {
    opsRoute: search.has('ops') ? normalizeOpsRoute(search.get('ops')) : 'chat',
  };
}

export function buildAiOpsHref(route?: OpsRoute): string {
  const opsRoute = route ?? 'chat';
  if (opsRoute === 'chat') {
    return ROUTES.aiOps;
  }
  const search = new URLSearchParams({
    ops: normalizeOpsRoute(opsRoute),
  });
  return `${ROUTES.aiOps}?${search.toString()}`;
}
