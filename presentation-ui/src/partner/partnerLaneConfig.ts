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
    eyebrow: 'Studio Ops Compat',
    title: 'Integrated Studio Ops surface',
    description: 'Studio Ops는 PBS 메인 랜딩을 유지한 채 compatibility lane으로 들어오고, 별도 workspace와 live OCP surface를 단계적으로 shared shell에 맞춥니다.',
    teammatePath: '/overview',
    launchLabel: 'Open Studio Ops overview',
    highlights: [
      'compat namespace /partner/*',
      'shared landing + shared shell',
      'ops overview entry',
    ],
    card: {
      icon: Boxes,
      title: 'Studio Ops Home',
      description: 'dashboard, workspace, library, live OCP 진입면',
    },
  },
  {
    path: ROUTES.partnerWorkspace,
    eyebrow: 'Studio Ops Workspace',
    title: 'Workspace and ops chat lane',
    description: '문서 근거와 live cluster 질의를 함께 다루는 Studio Ops workspace surface로 이동합니다.',
    teammatePath: '/chat',
    launchLabel: 'Open Studio Ops workspace',
    highlights: [
      'follow-up chat session rail',
      'workspace-aware connection state',
      'document + live cluster answer route',
    ],
  },
  {
    path: ROUTES.partnerLibrary,
    eyebrow: 'Studio Ops Library',
    title: 'Library and indexing lane',
    description: 'Studio Ops library, batch reindex, document preview 흐름으로 연결되는 compatibility page입니다.',
    teammatePath: '/library',
    launchLabel: 'Open Studio Ops library',
    highlights: [
      'document library',
      'batch reindex panel',
      'docs preview endpoints',
    ],
    card: {
      icon: FolderTree,
      title: 'Studio Ops Library',
      description: 'ops library / indexing page로 들어가는 compatibility lane',
    },
  },
  {
    path: ROUTES.partnerViewer,
    eyebrow: 'Studio Ops Live',
    title: 'Dashboard and live OCP lane',
    description: 'cluster overview, resources, actions 같은 live OCP surface를 Studio Ops compatibility lane에서 유지합니다.',
    teammatePath: '/overview',
    launchLabel: 'Open Studio Ops live ops',
    highlights: [
      'dashboard overview',
      'resources and YAML editor',
      'action approval workflow',
    ],
    card: {
      icon: MonitorPlay,
      title: 'Studio Ops Live',
      description: 'dashboard / resources / actions 흐름을 보존하는 ops lane',
    },
  },
  {
    path: ROUTES.partnerDetails,
    eyebrow: 'Studio Ops Details',
    title: 'Compatibility and launch details',
    description: 'Studio Ops 실행 경로, compatibility namespace, 단계적 통합 원칙을 확인하는 페이지입니다.',
    teammatePath: '/connections',
    launchLabel: 'Open Studio Ops connections',
    highlights: [
      'shared landing stays root',
      'compat route continuity',
      'separate ops runtime preserved',
    ],
  },
];

export const PARTNER_SURFACES = PARTNER_ROUTE_DEFINITIONS.filter(
  (route): route is PartnerRouteDefinition & { card: NonNullable<PartnerRouteDefinition['card']> } => Boolean(route.card),
);
