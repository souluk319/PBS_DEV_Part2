import { renderToStaticMarkup } from 'react-dom/server';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import Hero from './Hero';

describe('Hero', () => {
  it('renders the locked landing menu and CTA entry points', () => {
    const html = renderToStaticMarkup(
      <MemoryRouter initialEntries={['/']}>
        <Hero />
      </MemoryRouter>,
    );

    expect(html).toContain('Menu');
    expect(html).toContain('Studio');
    expect(html).toContain('AI Ops');
    expect(html).toContain('Launch Studio');
    expect(html).toContain('Demo 영상');
    expect(html).toContain('href="/studio"');
    expect(html).toContain('href="/aiops"');
    expect(html).not.toContain('Control Tower');
    expect(html).not.toContain('Shared Service Shell');
    expect(html).not.toContain('One service, two expert branches.');
    expect(html).not.toContain('compatibility');
    expect(html).not.toContain('lane');
  });
});
