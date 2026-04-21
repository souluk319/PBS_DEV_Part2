export type HandoffLocationLike = {
  search?: string;
  hash?: string;
};

export const HANDOFF_VERSION = '2026-04-21' as const;
export const HANDOFF_SEARCH_PARAM = 'handoff' as const;
const HANDOFF_BRANCHES = ['playbook', 'studio_ops', 'control_tower'] as const;
const HANDOFF_BOTS = ['playbot', 'ocp_ops_bot'] as const;
const HANDOFF_TRUTH_OWNERS = ['pbs', 'ops'] as const;
const HANDOFF_REASON_LABELS: Record<string, string> = {
  needs_live_cluster_context: '현재 클러스터 상태와 live resource 확인이 필요합니다.',
  needs_grounded_playbook_context: 'grounded playbook 절차와 citation 확인이 필요합니다.',
  needs_playbook_context: 'grounded playbook 절차와 citation 확인이 필요합니다.',
  continue_in_studio_ops: 'Studio Ops에서 운영 맥락을 이어서 확인합니다.',
  continue_in_playbook: 'Playbook에서 grounded 문서 맥락을 이어서 확인합니다.',
};

export type HandoffBranch = (typeof HANDOFF_BRANCHES)[number];
export type HandoffBot = (typeof HANDOFF_BOTS)[number];
export type HandoffTruthOwner = (typeof HANDOFF_TRUTH_OWNERS)[number];

export type HandoffPayload = {
  version: typeof HANDOFF_VERSION;
  handoffId: string;
  correlationId: string;
  parentHandoffId?: string;
  createdAt: string;
  sourceBranch: HandoffBranch;
  destinationBranch: HandoffBranch;
  fromBot: HandoffBot;
  toBot: HandoffBot;
  intentSummary: string;
  handoffReason: string;
  sourceSessionId?: string;
  sourceRoute?: string;
  boundaryTruth?: string;
  runtimeTruthLabel?: string;
  truthOwner?: HandoffTruthOwner;
  notes?: string[];
};

export type CreateHandoffPayloadInput = Omit<HandoffPayload, 'version' | 'handoffId' | 'correlationId' | 'createdAt'> & {
  handoffId?: string;
  correlationId?: string;
  createdAt?: string;
};

type SearchLike = string | URLSearchParams | null | undefined;

function isHandoffBranch(value: unknown): value is HandoffBranch {
  return typeof value === 'string' && HANDOFF_BRANCHES.includes(value as HandoffBranch);
}

function isHandoffBot(value: unknown): value is HandoffBot {
  return typeof value === 'string' && HANDOFF_BOTS.includes(value as HandoffBot);
}

function isHandoffTruthOwner(value: unknown): value is HandoffTruthOwner {
  return typeof value === 'string' && HANDOFF_TRUTH_OWNERS.includes(value as HandoffTruthOwner);
}

function randomToken(): string {
  if (typeof globalThis !== 'undefined' && globalThis.crypto && typeof globalThis.crypto.randomUUID === 'function') {
    return globalThis.crypto.randomUUID();
  }
  return Math.random().toString(36).slice(2, 10);
}

export function createHandoffCorrelationId(): string {
  return `handoff-${randomToken()}`;
}

export function createHandoffId(): string {
  return `hop-${randomToken()}`;
}

export function getHandoffBranchLabel(branch: HandoffBranch): string {
  if (branch === 'studio_ops') {
    return 'Studio Ops';
  }
  if (branch === 'control_tower') {
    return 'Control Tower';
  }
  return 'Playbook';
}

export function getHandoffBotLabel(bot: HandoffBot): string {
  return bot === 'ocp_ops_bot' ? 'OCP Ops bot' : 'Playbot';
}

export function getHandoffReasonLabel(reason: string): string {
  const normalized = String(reason || '').trim();
  if (!normalized) {
    return '다음 expert surface에서 이어서 확인이 필요합니다.';
  }
  return HANDOFF_REASON_LABELS[normalized] || normalized.replace(/_/g, ' ');
}

export function createHandoffPayload(input: CreateHandoffPayloadInput): HandoffPayload {
  return {
    version: HANDOFF_VERSION,
    handoffId: input.handoffId || createHandoffId(),
    correlationId: input.correlationId || createHandoffCorrelationId(),
    parentHandoffId: input.parentHandoffId?.trim() || undefined,
    createdAt: input.createdAt || new Date().toISOString(),
    sourceBranch: input.sourceBranch,
    destinationBranch: input.destinationBranch,
    fromBot: input.fromBot,
    toBot: input.toBot,
    intentSummary: input.intentSummary.trim(),
    handoffReason: input.handoffReason.trim(),
    sourceSessionId: input.sourceSessionId?.trim() || undefined,
    sourceRoute: input.sourceRoute?.trim() || undefined,
    boundaryTruth: input.boundaryTruth?.trim() || undefined,
    runtimeTruthLabel: input.runtimeTruthLabel?.trim() || undefined,
    truthOwner: input.truthOwner,
    notes: input.notes?.map((note) => note.trim()).filter(Boolean),
  };
}

export function createNextHandoffPayload(
  previous: HandoffPayload,
  input: Omit<CreateHandoffPayloadInput, 'correlationId' | 'parentHandoffId'>,
): HandoffPayload {
  return createHandoffPayload({
    ...input,
    correlationId: previous.correlationId,
    parentHandoffId: previous.handoffId,
  });
}

export function serializeHandoffPayload(payload: HandoffPayload): string {
  return JSON.stringify(payload);
}

export function parseHandoffPayload(value: string | null | undefined): HandoffPayload | null {
  if (!value) {
    return null;
  }

  try {
    const parsed = JSON.parse(value) as Partial<HandoffPayload> | null;
    if (!parsed || parsed.version !== HANDOFF_VERSION) {
      return null;
    }
    if (
      !isHandoffBranch(parsed.sourceBranch)
      || !isHandoffBranch(parsed.destinationBranch)
      || !isHandoffBot(parsed.fromBot)
      || !isHandoffBot(parsed.toBot)
      || typeof parsed.handoffId !== 'string'
      || typeof parsed.correlationId !== 'string'
      || typeof parsed.createdAt !== 'string'
      || typeof parsed.intentSummary !== 'string'
      || typeof parsed.handoffReason !== 'string'
    ) {
      return null;
    }
    if (parsed.truthOwner && !isHandoffTruthOwner(parsed.truthOwner)) {
      return null;
    }

    return createHandoffPayload({
      handoffId: parsed.handoffId,
      correlationId: parsed.correlationId,
      parentHandoffId: parsed.parentHandoffId,
      createdAt: parsed.createdAt,
      sourceBranch: parsed.sourceBranch,
      destinationBranch: parsed.destinationBranch,
      fromBot: parsed.fromBot,
      toBot: parsed.toBot,
      intentSummary: parsed.intentSummary,
      handoffReason: parsed.handoffReason,
      sourceSessionId: parsed.sourceSessionId,
      sourceRoute: parsed.sourceRoute,
      boundaryTruth: parsed.boundaryTruth,
      runtimeTruthLabel: parsed.runtimeTruthLabel,
      truthOwner: parsed.truthOwner,
      notes: parsed.notes,
    });
  } catch {
    return null;
  }
}

function normalizeSearchParams(searchLike: SearchLike): URLSearchParams {
  if (searchLike instanceof URLSearchParams) {
    return new URLSearchParams(searchLike);
  }
  if (typeof searchLike === 'string') {
    return new URLSearchParams(searchLike.startsWith('?') ? searchLike.slice(1) : searchLike);
  }
  return new URLSearchParams();
}

function searchParamsToString(searchParams: URLSearchParams): string {
  const rendered = searchParams.toString();
  return rendered ? `?${rendered}` : '';
}

export function readHandoffPayloadFromSearch(searchLike: SearchLike): HandoffPayload | null {
  return parseHandoffPayload(normalizeSearchParams(searchLike).get(HANDOFF_SEARCH_PARAM));
}

export function writeHandoffPayloadToSearch(searchLike: SearchLike, payload: HandoffPayload): string {
  const searchParams = normalizeSearchParams(searchLike);
  searchParams.set(HANDOFF_SEARCH_PARAM, serializeHandoffPayload(payload));
  return searchParamsToString(searchParams);
}

export function clearHandoffFromSearch(searchLike: SearchLike): string {
  const searchParams = normalizeSearchParams(searchLike);
  searchParams.delete(HANDOFF_SEARCH_PARAM);
  return searchParamsToString(searchParams);
}

export function buildHandoffLocation(pathname: string, locationLike: HandoffLocationLike) {
  return {
    pathname,
    search: locationLike.search || '',
    hash: locationLike.hash || '',
  };
}
