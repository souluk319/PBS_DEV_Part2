import { Boxes, FolderTree, MonitorPlay, type LucideIcon } from 'lucide-react';
import { ROUTES } from '../app/routes';

export type PartnerRouteDefinition = {
  path: string;
  eyebrow: string;
  title: string;
  description: string;
  teammatePath: string;
  launchLabel: string;
  highlights?: string[];
  card?: {
    icon: LucideIcon;
    title: string;
    description: string;
  };
};

export const PARTNER_ROUTE_DEFINITIONS: PartnerRouteDefinition[] = [
  {
    path: ROUTES.partnerHome,
    eyebrow: 'RAG Task Lane',
    title: 'Integrated teammate system',
    description: '팀원 과제 시스템은 PBS 메인 랜딩을 유지한 채 sibling lane으로 들어오고, 별도 workspace와 live OCP surface를 보존합니다.',
    teammatePath: '/overview',
    launchLabel: 'Open teammate overview',
    highlights: [
      'teammates/rag-task/apps/web',
      'teammates/rag-task/apps/api',
      'teammate/main @ e62074a',
    ],
    card: {
      icon: Boxes,
      title: 'RAG Task Home',
      description: '팀원 과제의 dashboard, chat, library, live OCP 진입면',
    },
  },
  {
    path: ROUTES.partnerWorkspace,
    eyebrow: 'RAG Task Chat',
    title: 'Chat and workspace lane',
    description: '문서 RAG와 live cluster 질의를 합친 teammate chat/workspace surface로 이동합니다.',
    teammatePath: '/chat',
    launchLabel: 'Open teammate chat',
    highlights: [
      'follow-up chat session rail',
      'workspace-aware connection state',
      'document + live cluster answer route',
    ],
  },
  {
    path: ROUTES.partnerLibrary,
    eyebrow: 'RAG Task Library',
    title: 'Library and indexing lane',
    description: 'teammate library, batch reindex, document preview 흐름으로 연결되는 sibling page입니다.',
    teammatePath: '/library',
    launchLabel: 'Open teammate library',
    highlights: [
      'document library',
      'batch reindex panel',
      'docs preview endpoints',
    ],
    card: {
      icon: FolderTree,
      title: 'RAG Task Library',
      description: 'teammate library / indexing page로 들어가는 별도 lane',
    },
  },
  {
    path: ROUTES.partnerViewer,
    eyebrow: 'RAG Task Live Ops',
    title: 'Dashboard and live OCP lane',
    description: 'cluster overview, resources, actions 같은 live OCP surface를 teammate 시스템 쪽에서 유지합니다.',
    teammatePath: '/overview',
    launchLabel: 'Open teammate live ops',
    highlights: [
      'dashboard overview',
      'resources and YAML editor',
      'action approval workflow',
    ],
    card: {
      icon: MonitorPlay,
      title: 'RAG Task Live Ops',
      description: 'dashboard / resources / actions 흐름을 보존하는 teammate lane',
    },
  },
  {
    path: ROUTES.partnerDetails,
    eyebrow: 'RAG Task Launch',
    title: 'Launch and repository details',
    description: 'teammate system 실행 경로, repo 위치, 분리 유지 원칙을 확인하는 페이지입니다.',
    teammatePath: '/connections',
    launchLabel: 'Open teammate connections',
    highlights: [
      'run web on a separate port',
      'keep PBS landing as root',
      'preserve teammate repo as sibling subtree',
    ],
  },
];

export const PARTNER_SURFACES = PARTNER_ROUTE_DEFINITIONS.filter(
  (route): route is PartnerRouteDefinition & { card: NonNullable<PartnerRouteDefinition['card']> } => Boolean(route.card),
);
