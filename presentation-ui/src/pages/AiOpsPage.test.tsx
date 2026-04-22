import { renderToStaticMarkup } from 'react-dom/server';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import AiOpsPage from './AiOpsPage';

describe('AiOpsPage', () => {
  it('mounts the standalone J original frontend instead of the integrated ops skin', () => {
    const html = renderToStaticMarkup(
      <MemoryRouter initialEntries={['/aiops?ops=overview']}>
        <AiOpsPage />
      </MemoryRouter>,
    );

    expect(html).toContain('iframe');
    expect(html).toContain('title="AI Ops"');
    expect(html).toContain('src="http://127.0.0.1:5174/overview"');
    expect(html).toContain('href="/"');
    expect(html).toContain('href="/studio"');
    expect(html).toContain('AI Ops');
  });

  it('defaults the public /aiops route to the chat entry when no explicit ops route is present', () => {
    const html = renderToStaticMarkup(
      <MemoryRouter initialEntries={['/aiops']}>
        <AiOpsPage />
      </MemoryRouter>,
    );

    expect(html).toContain('src="http://127.0.0.1:5174/chat"');
  });
});
