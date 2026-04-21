import { Layers3, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';
import { buildSharedLandingHref, type SharedLandingTab } from '../../app/routes';

export default function SharedLandingSwitcher({ activeTab }: { activeTab: SharedLandingTab }) {
  return (
    <div className="shared-shell-switcher glass-panel">
      <div>
        <div className="shared-shell-label">
          <Layers3 size={16} />
          <span>Shared Service Shell</span>
        </div>
        <h1 className="shared-shell-title">
          One service, two expert branches.
        </h1>
        <p className="shared-shell-description">
          PlayBook Studio는 메인 랜딩을 유지하고, Playbook과 Studio Ops를 같은 서비스 안에서
          분기합니다. PBS runtime truth와 route ownership은 유지하고, Studio Ops는 compatibility
          lane을 통해 단계적으로 통합합니다.
        </p>
      </div>
      <div className="shared-shell-tabs" aria-label="Product lane selector">
        <Link
          to={buildSharedLandingHref('pbs')}
          className={`shared-shell-tab ${activeTab === 'pbs' ? 'is-active' : ''}`}
        >
          <Sparkles size={16} />
          <span>Playbook</span>
        </Link>
        <Link
          to={buildSharedLandingHref('partner')}
          className={`shared-shell-tab ${activeTab === 'partner' ? 'is-active' : ''}`}
        >
          <Layers3 size={16} />
          <span>Studio Ops</span>
        </Link>
      </div>
    </div>
  );
}
