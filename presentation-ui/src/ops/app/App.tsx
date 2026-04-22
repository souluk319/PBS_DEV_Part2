import { Suspense, lazy, useEffect, useMemo, useState } from "react";

import { ChatSessionRail } from "@/domains/chat/ChatSessionRail";
import { createChatSessionRecord, deriveChatSessionTitle, type ChatSessionRecord } from "@/domains/chat/types";
import { ConnectionProfileMenu } from "@/domains/connection/ConnectionProfileMenu";
import { useOcpConnection } from "@/domains/connection/useOcpConnection";
import { setOpsApiBaseUrl } from "@/domains/apiBase";
import type { WorkspaceRecord } from "@/domains/workspaces/types";
import { listWorkspaces } from "@/domains/workspaces/workspacesApi";
import { AppShell } from "@/shared/layout/AppShell";
import { Button } from "@/shared/ui/button";
import type { OpsRoute } from "./routes";
import {
  getHandoffBotLabel,
  getHandoffBranchLabel,
  getHandoffReasonLabel,
  type HandoffPayload,
} from "../../app/handoff";

const CHAT_SESSIONS_STORAGE_KEY = "rag-task.chat.sessions";
const ACTIVE_WORKSPACE_STORAGE_KEY = "rag-task.workspace.active";
const NO_ACTIVE_WORKSPACE = "__none__";

const WorkspacesPage = lazy(() => import("../pages/WorkspacesPage").then((module) => ({ default: module.WorkspacesPage })));
const ConnectionPage = lazy(() => import("../pages/ConnectionPage").then((module) => ({ default: module.ConnectionPage })));
const ModelsPage = lazy(() => import("../pages/ModelsPage").then((module) => ({ default: module.ModelsPage })));
const DashboardPage = lazy(() => import("../pages/DashboardPage").then((module) => ({ default: module.DashboardPage })));
const ResourcesPage = lazy(() => import("../pages/ResourcesPage").then((module) => ({ default: module.ResourcesPage })));
const LibraryPage = lazy(() => import("../pages/LibraryPage").then((module) => ({ default: module.LibraryPage })));
const ChatPage = lazy(() => import("../pages/ChatPage").then((module) => ({ default: module.ChatPage })));
const ActionsPage = lazy(() => import("../pages/ActionsPage").then((module) => ({ default: module.ActionsPage })));
const ScmPage = lazy(() => import("../pages/ScmPage").then((module) => ({ default: module.ScmPage })));

type GlobalLoadingState = {
  active: boolean;
  title: string;
  detail?: string;
};

type OpsAppProps = {
  route: OpsRoute;
  onNavigate: (route: OpsRoute) => void;
  apiBaseUrl?: string;
  handoff?: HandoffPayload | null;
  onDismissHandoff?: () => void;
  onReturnToPlaybook?: (context?: { sourceSessionId?: string; intentSummary?: string; sourceRoute?: string }) => void;
};

function loadChatSessions(): ChatSessionRecord[] {
  if (typeof window === "undefined") return [createChatSessionRecord()];
  try {
    const raw = window.localStorage.getItem(CHAT_SESSIONS_STORAGE_KEY);
    if (!raw) return [createChatSessionRecord()];
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed) || parsed.length === 0) return [createChatSessionRecord()];
    return parsed as ChatSessionRecord[];
  } catch {
    return [createChatSessionRecord()];
  }
}

export function App({
  route,
  onNavigate,
  apiBaseUrl,
  handoff,
  onDismissHandoff,
  onReturnToPlaybook,
}: OpsAppProps) {
  const [selectedWorkspaceId, setSelectedWorkspaceId] = useState<string>(() => {
    if (typeof window === "undefined") return "";
    const stored = window.localStorage.getItem(ACTIVE_WORKSPACE_STORAGE_KEY) ?? "";
    return stored === NO_ACTIVE_WORKSPACE ? "" : stored;
  });
  const connectionController = useOcpConnection(selectedWorkspaceId);
  const [chatSessions, setChatSessions] = useState<ChatSessionRecord[]>(() => loadChatSessions());
  const [activeChatSessionId, setActiveChatSessionId] = useState<string>("");
  const [workspaceSnapshot, setWorkspaceSnapshot] = useState<WorkspaceRecord[]>([]);
  const [pageLoadingState, setPageLoadingState] = useState<GlobalLoadingState>({
    active: false,
    title: "",
  });

  useEffect(() => {
    setOpsApiBaseUrl(apiBaseUrl);
  }, [apiBaseUrl]);

  useEffect(() => {
    window.localStorage.setItem(CHAT_SESSIONS_STORAGE_KEY, JSON.stringify(chatSessions));
  }, [chatSessions]);

  useEffect(() => {
    if (typeof window === "undefined") return;
    window.localStorage.setItem(
      ACTIVE_WORKSPACE_STORAGE_KEY,
      selectedWorkspaceId || NO_ACTIVE_WORKSPACE,
    );
  }, [selectedWorkspaceId]);

  useEffect(() => {
    if (!activeChatSessionId && chatSessions[0]) {
      setActiveChatSessionId(chatSessions[0].id);
      return;
    }
    if (!chatSessions.some((session) => session.id === activeChatSessionId)) {
      setActiveChatSessionId(chatSessions[0]?.id ?? createChatSessionRecord().id);
    }
  }, [activeChatSessionId, chatSessions]);

  useEffect(() => {
    async function run() {
      try {
        const next = await listWorkspaces();
        setWorkspaceSnapshot(next);
        const stored = typeof window === "undefined" ? "" : window.localStorage.getItem(ACTIVE_WORKSPACE_STORAGE_KEY) ?? "";
        if (!selectedWorkspaceId && next[0] && stored !== NO_ACTIVE_WORKSPACE) {
          setSelectedWorkspaceId(next[0].workspaceId);
        }
      } catch {
        setWorkspaceSnapshot([]);
      }
    }
    void run();
  }, [selectedWorkspaceId]);

  useEffect(() => {
    if (!handoff || handoff.destinationBranch !== "studio_ops") {
      return;
    }

    let nextActiveSessionId = "";
    setChatSessions((current) => {
      const existing = current.find((session) => session.handoff?.handoffId === handoff.handoffId);
      if (existing) {
        nextActiveSessionId = existing.id;
        return current.map((session) =>
          session.id === existing.id
            ? {
                ...session,
                handoff,
              }
            : session,
        );
      }

      const nextSession = createChatSessionRecord({
        title: deriveChatSessionTitle(handoff.intentSummary),
        handoff,
      });
      nextActiveSessionId = nextSession.id;
      return [nextSession, ...current];
    });

    if (nextActiveSessionId) {
      setActiveChatSessionId(nextActiveSessionId);
    }
  }, [handoff]);

  const activeChatSession = useMemo(
    () => chatSessions.find((session) => session.id === activeChatSessionId) ?? chatSessions[0] ?? createChatSessionRecord(),
    [activeChatSessionId, chatSessions],
  );
  const activeHandoff = activeChatSession.handoff ?? (handoff?.destinationBranch === "studio_ops" ? handoff : null);
  const selectedWorkspace = useMemo(
    () => workspaceSnapshot.find((item) => item.workspaceId === selectedWorkspaceId) ?? null,
    [selectedWorkspaceId, workspaceSnapshot],
  );

  function createChatSession() {
    const nextSession = createChatSessionRecord();
    setChatSessions((current) => [nextSession, ...current]);
    setActiveChatSessionId(nextSession.id);
    onNavigate("chat");
  }

  function clearActiveWorkspace() {
    setSelectedWorkspaceId("");
  }

  function selectChatSession(sessionId: string) {
    setActiveChatSessionId(sessionId);
    onNavigate("chat");
  }

  function removeChatSession(sessionId: string) {
    setChatSessions((current) => {
      const next = current.filter((session) => session.id !== sessionId);
      return next.length > 0 ? next : [createChatSessionRecord()];
    });
  }

  function updateChatSession(sessionId: string, updater: (current: ChatSessionRecord) => ChatSessionRecord) {
    setChatSessions((current) => current.map((session) => (session.id === sessionId ? updater(session) : session)));
  }

  function clearHandoffFromSessions(handoffId?: string) {
    if (!handoffId) {
      return;
    }
    setChatSessions((current) =>
      current.map((session) =>
        session.handoff?.handoffId === handoffId
          ? {
              ...session,
              handoff: null,
            }
          : session,
      ),
    );
  }

  function summarizeOpsIntent(currentSession: ChatSessionRecord): string {
    const latestUserTurn = [...currentSession.turns].reverse().find((turn) => turn.role === "user")?.text?.trim();
    if (latestUserTurn) {
      return latestUserTurn;
    }
    if (currentSession.handoff?.intentSummary) {
      return currentSession.handoff.intentSummary;
    }
    if (route === "resources") {
      return "현재 리소스 상태와 연결된 grounded playbook을 확인해줘";
    }
    if (route === "overview") {
      return "현재 클러스터 overview에 맞는 grounded playbook guidance를 보여줘";
    }
    return "현재 운영 흐름에 맞는 grounded playbook guidance를 이어서 확인해줘";
  }

  function handleDismissActiveHandoff() {
    clearHandoffFromSessions(activeHandoff?.handoffId);
    onDismissHandoff?.();
  }

  function handleReturnToPlaybook() {
    onReturnToPlaybook?.({
      sourceSessionId: activeChatSession.id,
      intentSummary: summarizeOpsIntent(activeChatSession),
      sourceRoute: activeHandoff?.sourceRoute,
    });
  }

  const shellLoadingState = useMemo<GlobalLoadingState>(() => {
    if (connectionController.isBusy) {
      const title =
        connectionController.submitState === "connecting"
          ? "클러스터 연결 중"
          : connectionController.submitState === "testing"
            ? "연결 상태 검증 중"
            : connectionController.submitState === "disconnecting"
              ? "세션 정리 중"
              : "처리 중";
      return { active: true, title, detail: connectionController.message };
    }
    return pageLoadingState;
  }, [connectionController.isBusy, connectionController.message, connectionController.submitState, pageLoadingState]);

  const page = useMemo(() => {
    switch (route) {
      case "workspaces":
        return (
          <WorkspacesPage
            selectedWorkspaceId={selectedWorkspaceId}
            onSelectWorkspace={setSelectedWorkspaceId}
            onClearWorkspace={clearActiveWorkspace}
            onLoadingChange={setPageLoadingState}
          />
        );
      case "chat":
        return (
          <ChatPage
            controller={connectionController}
            session={activeChatSession}
            updateSession={updateChatSession}
            incomingHandoff={activeChatSession.handoff ?? null}
            onDismissHandoff={handleDismissActiveHandoff}
          />
        );
      case "models":
        return <ModelsPage selectedWorkspace={selectedWorkspace} onLoadingChange={setPageLoadingState} />;
      case "overview":
        return <DashboardPage controller={connectionController} selectedWorkspace={selectedWorkspace} onLoadingChange={setPageLoadingState} />;
      case "resources":
        return <ResourcesPage controller={connectionController} selectedWorkspace={selectedWorkspace} onLoadingChange={setPageLoadingState} />;
      case "library":
        return <LibraryPage controller={connectionController} selectedWorkspace={selectedWorkspace} onLoadingChange={setPageLoadingState} />;
      case "scm":
        return <ScmPage selectedWorkspace={selectedWorkspace} onLoadingChange={setPageLoadingState} />;
      case "actions":
        return <ActionsPage controller={connectionController} />;
      case "connections":
      default:
        return <ConnectionPage controller={connectionController} selectedWorkspace={selectedWorkspace} />;
    }
  }, [activeChatSession, connectionController, route, selectedWorkspace, selectedWorkspaceId]);

  const railContent = useMemo(() => {
    if (route !== "chat") return null;
    return (
      <ChatSessionRail
        sessions={chatSessions}
        activeSessionId={activeChatSession.id}
        onSelect={selectChatSession}
        onCreate={createChatSession}
        onRemove={removeChatSession}
      />
    );
  }, [activeChatSession.id, chatSessions, route]);

  const footerContent = useMemo(
    () => (
      <ConnectionProfileMenu
        controller={connectionController}
        onOpenConnections={() => onNavigate("connections")}
      />
    ),
    [connectionController, onNavigate],
  );

  const shellBanner = activeHandoff ? (
    <div className="rounded-2xl border border-primary/25 bg-primary/10 px-4 py-4">
      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div className="space-y-1">
          <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-primary">
            PlayBook Studio Handoff
          </div>
          <div className="text-base font-semibold text-foreground">
            {getHandoffBotLabel(activeHandoff.fromBot)}
            {" -> "}
            {getHandoffBranchLabel(activeHandoff.destinationBranch)}
          </div>
          <div className="max-w-3xl text-sm leading-6 text-muted-foreground">
            {getHandoffReasonLabel(activeHandoff.handoffReason)}
          </div>
          <div className="text-xs text-muted-foreground">
            summary: {activeHandoff.intentSummary}
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          {route !== "chat" ? (
            <Button type="button" size="sm" variant="secondary" onClick={() => onNavigate("chat")}>
              Resume in Chat
            </Button>
          ) : null}
          <Button type="button" size="sm" variant="outline" onClick={handleReturnToPlaybook}>
            Return to Playbook
          </Button>
          <Button type="button" size="sm" variant="ghost" onClick={handleDismissActiveHandoff}>
            Dismiss
          </Button>
        </div>
      </div>
    </div>
  ) : null;

  return (
    <AppShell
      activeRoute={route}
      onNavigate={onNavigate}
      profile={connectionController.profile}
      testResult={connectionController.testResult}
      schedulerStatus={connectionController.schedulerStatus}
      message={connectionController.message}
      railContent={railContent}
      footerContent={footerContent}
      topBanner={shellBanner}
      loadingState={shellLoadingState}
    >
      <Suspense fallback={<div className="surface-muted rounded-xl px-4 py-3 text-sm text-muted-foreground">페이지를 불러오는 중입니다.</div>}>
        {page}
      </Suspense>
    </AppShell>
  );
}
