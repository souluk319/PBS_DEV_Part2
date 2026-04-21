import { renderToStaticMarkup } from 'react-dom/server';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import WorkspaceHeader from './WorkspaceHeader';

describe('WorkspaceHeader', () => {
  it('renders quick navigation buttons for landing and AI Ops from the studio page header', () => {
    const html = renderToStaticMarkup(
      <MemoryRouter>
        <WorkspaceHeader
          packDropdownOpen={false}
          packLabel="OpenShift 4.20"
          packOptions={['OpenShift 4.20']}
          sessionId="sess-1234"
          surfaceMode="pbs"
          testMode={false}
          globalTheme="dark"
          onOpenLanding={vi.fn()}
          onOpenPlaybook={vi.fn()}
          onOpenStudioOps={vi.fn()}
          onOpenLibrary={vi.fn()}
          onResetSession={vi.fn()}
          onSelectPack={vi.fn()}
          onTogglePackDropdown={vi.fn()}
          onToggleTestMode={vi.fn()}
          onToggleGlobalTheme={vi.fn()}
        />
      </MemoryRouter>,
    );

    expect(html).toContain('Landing');
    expect(html).toContain('Playbook');
    expect(html).toContain('AI Ops');
  });
});
