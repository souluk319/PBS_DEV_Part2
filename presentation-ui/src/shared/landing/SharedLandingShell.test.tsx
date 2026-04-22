import { renderToStaticMarkup } from 'react-dom/server';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import SharedLandingShell from './SharedLandingShell';

vi.mock('../../pages/LandingPage', () => ({
  default: function MockLandingPage() {
    return <div>pbs landing body</div>;
  },
}));

describe('SharedLandingShell', () => {
  it('renders only the landing body without the old shared-shell copy', () => {
    const html = renderToStaticMarkup(
      <MemoryRouter initialEntries={['/']}>
        <SharedLandingShell />
      </MemoryRouter>,
    );

    expect(html).toContain('pbs landing body');
    expect(html).not.toContain('One service, two expert branches.');
    expect(html).not.toContain('Shared Service Shell');
    expect(html).not.toContain('compatibility');
  });
});
