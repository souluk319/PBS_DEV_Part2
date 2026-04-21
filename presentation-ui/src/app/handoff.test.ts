import { describe, expect, it } from 'vitest';
import {
  HANDOFF_VERSION,
  HANDOFF_SEARCH_PARAM,
  buildHandoffLocation,
  createHandoffCorrelationId,
  createNextHandoffPayload,
  createHandoffPayload,
  readHandoffPayloadFromSearch,
  clearHandoffFromSearch,
  parseHandoffPayload,
  serializeHandoffPayload,
  writeHandoffPayloadToSearch,
} from './handoff';

describe('buildHandoffLocation', () => {
  it('preserves search and hash during alias handoff', () => {
    expect(
      buildHandoffLocation('/studio', {
        search: '?surface=ops&ops=overview',
        hash: '#top',
      }),
    ).toEqual({
      pathname: '/studio',
      search: '?surface=ops&ops=overview',
      hash: '#top',
    });
  });

  it('falls back to empty search and hash when absent', () => {
    expect(buildHandoffLocation('/llmwikibook', {})).toEqual({
      pathname: '/llmwikibook',
      search: '',
      hash: '',
    });
  });
});

describe('handoff payload helpers', () => {
  it('creates a correlation id with the handoff prefix', () => {
    expect(createHandoffCorrelationId()).toMatch(/^handoff-/);
  });

  it('creates a typed payload with integration defaults', () => {
    const payload = createHandoffPayload({
      correlationId: 'handoff-fixed',
      createdAt: '2026-04-21T00:00:00.000Z',
      sourceBranch: 'playbook',
      destinationBranch: 'studio_ops',
      fromBot: 'playbot',
      toBot: 'ocp_ops_bot',
      intentSummary: ' Check current cluster state ',
      handoffReason: ' needs_live_cluster_context ',
      truthOwner: 'ops',
      notes: [' cluster verification ', ' source handoff '],
    });

    expect(payload).toEqual({
      version: HANDOFF_VERSION,
      handoffId: payload.handoffId,
      correlationId: 'handoff-fixed',
      createdAt: '2026-04-21T00:00:00.000Z',
      sourceBranch: 'playbook',
      destinationBranch: 'studio_ops',
      fromBot: 'playbot',
      toBot: 'ocp_ops_bot',
      intentSummary: 'Check current cluster state',
      handoffReason: 'needs_live_cluster_context',
      truthOwner: 'ops',
      notes: ['cluster verification', 'source handoff'],
    });
    expect(payload.handoffId).toMatch(/^hop-/);
  });

  it('round-trips a serialized payload', () => {
    const payload = createHandoffPayload({
      handoffId: 'hop-fixed',
      correlationId: 'handoff-fixed',
      createdAt: '2026-04-21T00:00:00.000Z',
      sourceBranch: 'studio_ops',
      destinationBranch: 'playbook',
      fromBot: 'ocp_ops_bot',
      toBot: 'playbot',
      intentSummary: 'Open the canonical playbook',
      handoffReason: 'needs_grounded_procedure',
      sourceSessionId: 'ops-session-1',
      sourceRoute: '/studio?surface=ops&ops=chat',
      boundaryTruth: 'official_validated_runtime',
      runtimeTruthLabel: 'PBS runtime',
      truthOwner: 'pbs',
    });

    expect(parseHandoffPayload(serializeHandoffPayload(payload))).toEqual(payload);
  });

  it('creates the next hop while preserving correlation id', () => {
    const first = createHandoffPayload({
      handoffId: 'hop-1',
      correlationId: 'handoff-fixed',
      createdAt: '2026-04-21T00:00:00.000Z',
      sourceBranch: 'playbook',
      destinationBranch: 'studio_ops',
      fromBot: 'playbot',
      toBot: 'ocp_ops_bot',
      intentSummary: 'Check the cluster state',
      handoffReason: 'needs_live_cluster_context',
      truthOwner: 'ops',
    });

    const second = createNextHandoffPayload(first, {
      handoffId: 'hop-2',
      createdAt: '2026-04-21T00:01:00.000Z',
      sourceBranch: 'studio_ops',
      destinationBranch: 'playbook',
      fromBot: 'ocp_ops_bot',
      toBot: 'playbot',
      intentSummary: 'Open the grounded playbook',
      handoffReason: 'needs_grounded_playbook_context',
      truthOwner: 'pbs',
    });

    expect(second.correlationId).toBe('handoff-fixed');
    expect(second.parentHandoffId).toBe('hop-1');
    expect(second.handoffId).toBe('hop-2');
  });

  it('writes, reads, and clears a handoff payload from search params', () => {
    const payload = createHandoffPayload({
      handoffId: 'hop-fixed',
      correlationId: 'handoff-fixed',
      createdAt: '2026-04-21T00:00:00.000Z',
      sourceBranch: 'playbook',
      destinationBranch: 'studio_ops',
      fromBot: 'playbot',
      toBot: 'ocp_ops_bot',
      intentSummary: 'Check the cluster state',
      handoffReason: 'needs_live_cluster_context',
      sourceRoute: '/studio',
      truthOwner: 'ops',
    });

    const search = writeHandoffPayloadToSearch('?surface=ops&ops=chat', payload);
    expect(search).toContain(`surface=ops`);
    expect(search).toContain(HANDOFF_SEARCH_PARAM);
    expect(readHandoffPayloadFromSearch(search)).toEqual(payload);
    expect(clearHandoffFromSearch(search)).toBe('?surface=ops&ops=chat');
  });

  it('returns null for invalid serialized payloads', () => {
    expect(parseHandoffPayload('{"version":"2026-04-21","sourceBranch":"invalid"}')).toBeNull();
    expect(parseHandoffPayload('{"version":"2026-04-18","handoffId":"hop-1"}')).toBeNull();
    expect(parseHandoffPayload('not-json')).toBeNull();
    expect(parseHandoffPayload('')).toBeNull();
  });
});
