import { ArrowLeftRight, ExternalLink, FolderGit2, PlaySquare, ShieldCheck, SplitSquareVertical } from 'lucide-react';
import { Link } from 'react-router-dom';
import { buildSharedLandingHref } from '../app/routes';
import './PartnerNamespacePage.css';

type PartnerNamespacePageProps = {
  eyebrow: string;
  title: string;
  description: string;
  teammatePath: string;
  launchLabel: string;
  highlights?: string[];
};

const DEFAULT_TEAMMATE_APP_URL = 'http://127.0.0.1:4174';

export default function PartnerNamespacePage({
  eyebrow,
  title,
  description,
  teammatePath,
  launchLabel,
  highlights = [],
}: PartnerNamespacePageProps) {
  const teammateBaseUrl = (import.meta.env.VITE_TEAMMATE_APP_URL || DEFAULT_TEAMMATE_APP_URL).trim().replace(/\/$/, '');
  const launchUrl = `${teammateBaseUrl}${teammatePath}`;

  return (
    <div className="partner-namespace-page">
      <div className="partner-namespace-shell">
        <Link to={buildSharedLandingHref('partner')} className="partner-namespace-back">
          <ArrowLeftRight size={18} />
          <span>Back to Shared Landing</span>
        </Link>

        <section className="partner-namespace-card glass-panel">
          <span className="partner-namespace-eyebrow">{eyebrow}</span>
          <h1 className="partner-namespace-title">{title}</h1>
          <p className="partner-namespace-description">{description}</p>
          <div className="partner-namespace-actions">
            <a href={launchUrl} target="_blank" rel="noreferrer" className="partner-namespace-primary">
              <PlaySquare size={18} />
              <span>{launchLabel}</span>
            </a>
            <a href="https://github.com/JungyuOO/RAG_Task" target="_blank" rel="noreferrer" className="partner-namespace-secondary">
              <ExternalLink size={18} />
              <span>Open teammate repo</span>
            </a>
          </div>
        </section>

        <div className="partner-namespace-grid">
          <section className="glass-panel">
            <SplitSquareVertical size={22} />
            <h3>Launch target</h3>
            <p>
              teammate web app는 별도 포트에서 실행하고, PBS는 이 sibling lane에서 진입만 담당합니다.
            </p>
            <code className="partner-namespace-code">{launchUrl}</code>
          </section>
          <section className="glass-panel">
            <ShieldCheck size={22} />
            <h3>Truth isolation</h3>
            <p>
              shared landing은 entry shell만 공유합니다. PBS runtime truth와 teammate system state는 분리 유지합니다.
            </p>
          </section>
          <section className="glass-panel">
            <FolderGit2 size={22} />
            <h3>Integrated subtree</h3>
            <p>
              teammate source는 integration repo 내부
              <strong> `teammates/rag-task` </strong>
              아래에 그대로 보존했습니다.
            </p>
            <code className="partner-namespace-code">teammates/rag-task/apps/web</code>
            <code className="partner-namespace-code">teammates/rag-task/apps/api</code>
          </section>
          <section className="glass-panel">
            <PlaySquare size={22} />
            <h3>Run notes</h3>
            <p>
              teammate app preview가 필요하면 web은 별도 포트에서 실행하고, PBS 메인 앱은 그대로 둡니다.
            </p>
            <code className="partner-namespace-code">cd teammates/rag-task/apps/web</code>
            <code className="partner-namespace-code">npm run dev -- --port 4174</code>
          </section>
        </div>

        {highlights.length > 0 ? (
          <section className="partner-namespace-highlights glass-panel">
            <h3>Lane summary</h3>
            <ul>
              {highlights.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </section>
        ) : null}

        <section className="partner-namespace-preview glass-panel">
          <div className="partner-namespace-preview-head">
            <div>
              <span className="partner-namespace-eyebrow">Embedded Preview</span>
              <h3>{title}</h3>
            </div>
            <a href={launchUrl} target="_blank" rel="noreferrer" className="partner-namespace-secondary">
              <ExternalLink size={18} />
              <span>Open in new tab</span>
            </a>
          </div>
          <p className="partner-namespace-preview-copy">
            teammate web app가 실행 중이면 아래 iframe에서 바로 확인할 수 있습니다.
          </p>
          <div className="partner-namespace-frame-wrap">
            <iframe
              title={`${title} preview`}
              src={launchUrl}
              className="partner-namespace-frame"
            />
          </div>
        </section>
      </div>
    </div>
  );
}
