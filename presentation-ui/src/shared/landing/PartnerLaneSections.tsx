import { ArrowRight, Waypoints } from 'lucide-react';
import { Link } from 'react-router-dom';
import { ROUTES } from '../../app/routes';
import { PARTNER_SURFACES } from '../../partner/partnerLaneConfig';

export function PartnerLaneHero() {
  return (
    <div className="partner-lane-hero glass-panel">
      <div className="partner-lane-copy">
        <span className="partner-lane-eyebrow">RAG Task Lane</span>
        <h2 className="partner-lane-title">PBS root stays. Teammate system joins as a new lane.</h2>
        <p className="partner-lane-description">
          팀원 과제는 shared landing에서 새 페이지로 연결되지만, 실제 기능 surface는
          <strong> `/partner/*` </strong>
          아래에서 분기됩니다. PBS 메인 랜딩과 core route family는 유지하고,
          teammate chat, dashboard, library, live OCP surface만 sibling lane으로 붙입니다.
        </p>
      </div>
      <div className="partner-lane-actions">
        <Link to={ROUTES.partnerHome} className="partner-primary-link">
          <span>Open RAG Task Lane</span>
          <ArrowRight size={18} />
        </Link>
        <Link to={ROUTES.partnerDetails} className="partner-secondary-link">
          Launch Details
        </Link>
      </div>
    </div>
  );
}

export function PartnerSurfaceGrid() {
  return (
    <div className="partner-surface-grid">
      {PARTNER_SURFACES.map(({ path, card }) => {
        const Icon = card.icon;
        return (
          <Link key={path} to={path} className="partner-surface-card glass-panel">
            <div className="partner-surface-icon">
              <Icon size={26} />
            </div>
            <h3>{card.title}</h3>
            <p>{card.description}</p>
          </Link>
        );
      })}
    </div>
  );
}

export function PartnerGuardRail() {
  return (
    <div className="partner-lane-guard glass-panel">
      <div className="partner-lane-guard-icon">
        <Waypoints size={22} />
      </div>
      <div>
        <h3>Merge-ready guardrail</h3>
        <p>
          PBS는 기존 경로
          <strong> `/studio`, `/llmwikibook`, `/playbook-library*` </strong>
          를 그대로 유지하고, teammate 시스템은 subtree + sibling lane으로 받아들입니다.
        </p>
      </div>
    </div>
  );
}
