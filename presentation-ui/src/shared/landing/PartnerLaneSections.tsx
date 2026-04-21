import { ArrowRight, Waypoints } from 'lucide-react';
import { Link } from 'react-router-dom';
import { ROUTES } from '../../app/routes';
import { PARTNER_SURFACES } from '../../partner/partnerLaneConfig';

export function PartnerLaneHero() {
  return (
    <div className="partner-lane-hero glass-panel">
      <div className="partner-lane-copy">
        <span className="partner-lane-eyebrow">Studio Ops Compatibility</span>
        <h2 className="partner-lane-title">PBS root stays. Studio Ops joins through a compatibility lane.</h2>
        <p className="partner-lane-description">
          Studio Ops는 shared landing에서 분기되지만, 현재 단계의 실제 기능 surface는
          <strong> `/partner/*` </strong>
          아래에서 호환 레인으로 열립니다. PBS 메인 랜딩과 core route family는 유지하고,
          ops chat, dashboard, library, live OCP surface만 compatibility subtree로 연결합니다.
        </p>
      </div>
      <div className="partner-lane-actions">
        <Link to={ROUTES.partnerHome} className="partner-primary-link">
          <span>Open Studio Ops Lane</span>
          <ArrowRight size={18} />
        </Link>
        <Link to={ROUTES.partnerDetails} className="partner-secondary-link">
          Compatibility Details
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
        <h3>Integration guardrail</h3>
        <p>
          PBS는 기존 경로
          <strong> `/studio`, `/llmwikibook`, `/playbook-library*` </strong>
          를 그대로 유지하고, Studio Ops는 compatibility subtree와 shared shell을 함께 사용합니다.
        </p>
      </div>
    </div>
  );
}
