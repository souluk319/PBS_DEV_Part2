import { describe, expect, it } from 'vitest';
import {
  buildAiOpsHref,
  buildSharedLandingHref,
  buildStudioHref,
  readAiOpsRouteState,
  readStudioSurfaceState,
  ROUTES,
} from './routes';

describe('public route helpers', () => {
  it('keeps the landing root canonical for shared-home links', () => {
    expect(buildSharedLandingHref('partner')).toBe('/');
    expect(buildSharedLandingHref('pbs')).toBe('/');
  });

  it('keeps /studio as the playbook page by default', () => {
    expect(readStudioSurfaceState('')).toEqual({
      surfaceMode: 'pbs',
      opsRoute: 'overview',
    });
  });

  it('normalizes the ops studio surface query', () => {
    expect(readStudioSurfaceState('?surface=ops&ops=chat')).toEqual({
      surfaceMode: 'ops',
      opsRoute: 'chat',
    });
  });

  it('falls back to the default ops route for stale resume links', () => {
    expect(readStudioSurfaceState('?surface=ops&ops=bogus')).toEqual({
      surfaceMode: 'ops',
      opsRoute: 'overview',
    });
  });

  it('keeps the legacy studio ops href builder for compatibility redirects only', () => {
    expect(buildStudioHref({ surfaceMode: 'ops', opsRoute: 'library' })).toBe(
      '/studio?surface=ops&ops=library',
    );
  });

  it('falls back to the base studio href for the playbook surface', () => {
    expect(buildStudioHref({ surfaceMode: 'pbs', opsRoute: 'chat' })).toBe('/studio');
    expect(buildStudioHref()).toBe('/studio');
  });

  it('exposes /aiops as the public ops route and defaults it to chat', () => {
    expect(ROUTES.aiOps).toBe('/aiops');
    expect(readAiOpsRouteState('')).toEqual({
      opsRoute: 'chat',
    });
    expect(buildAiOpsHref()).toBe('/aiops');
    expect(buildAiOpsHref('chat')).toBe('/aiops');
    expect(buildAiOpsHref('overview')).toBe('/aiops?ops=overview');
  });

  it('normalizes explicit aiops subroutes and falls back stale links to overview', () => {
    expect(readAiOpsRouteState('?ops=library')).toEqual({
      opsRoute: 'library',
    });
    expect(readAiOpsRouteState('?ops=bogus')).toEqual({
      opsRoute: 'overview',
    });
  });
});
