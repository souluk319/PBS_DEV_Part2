import { useEffect, useRef, useState } from 'react';
import gsap from 'gsap';
import { Link } from 'react-router-dom';
import { Sparkles, ArrowRight, Languages, Menu, ChevronDown } from 'lucide-react';
import { ROUTES } from '../app/routes';
import './Hero.css';

export default function Hero() {
  const containerRef = useRef<HTMLDivElement>(null);
  const maskRef = useRef<HTMLDivElement>(null);
  const textGroupRef = useRef<HTMLDivElement>(null);
  const menuRef = useRef<HTMLDivElement>(null);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Cinematic Entrance: Scale down from 1.1 + fade in
      gsap.fromTo(textGroupRef.current,
        { autoAlpha: 0, scale: 1.1, translateY: 30 },
        { autoAlpha: 1, scale: 1, translateY: 0, duration: 2.2, ease: "power4.out", delay: 0.1 }
      );

      // Background mask reveal effect on scroll
      gsap.to(maskRef.current, {
        scrollTrigger: {
          trigger: containerRef.current,
          start: "top top",
          end: "bottom top",
          scrub: 1,
        },
        clipPath: "circle(100% at 50% 50%)"
      });

    }, containerRef);
    return () => ctx.revert();
  }, []);

  useEffect(() => {
    function handlePointerDown(event: MouseEvent) {
      if (!menuRef.current?.contains(event.target as Node)) {
        setMenuOpen(false);
      }
    }

    window.addEventListener('mousedown', handlePointerDown);
    return () => {
      window.removeEventListener('mousedown', handlePointerDown);
    };
  }, []);

  return (
    <section className="hero-container" ref={containerRef}>
      <div className="hero-nav">
        <div className="hero-menu" ref={menuRef}>
          <button
            type="button"
            className="hero-menu-trigger"
            aria-expanded={menuOpen}
            aria-controls="landing-primary-menu"
            onClick={() => setMenuOpen((current) => !current)}
          >
            <Menu size={18} />
            <span>Menu</span>
            <ChevronDown size={16} className={`hero-menu-chevron ${menuOpen ? 'open' : ''}`} />
          </button>
          <div
            id="landing-primary-menu"
            className={`hero-menu-popover ${menuOpen ? 'is-open' : ''}`}
            role="menu"
            aria-label="Landing primary menu"
          >
            <Link
              to={ROUTES.pbsStudio}
              className="hero-menu-link"
              role="menuitem"
              onClick={() => setMenuOpen(false)}
            >
              <span>Studio</span>
              <ArrowRight size={15} />
            </Link>
            <Link
              to={ROUTES.aiOps}
              className="hero-menu-link"
              role="menuitem"
              onClick={() => setMenuOpen(false)}
            >
              <span>AI Ops</span>
              <ArrowRight size={15} />
            </Link>
          </div>
        </div>
        <button className="lang-btn" type="button">
          <Languages size={18} />
          <span>KOR</span>
        </button>
      </div>
      <div className="hero-bokeh bokeh-cyan"></div>
      <div className="hero-bokeh bokeh-purple"></div>

      {/* Background Masking Layer */}
      <div className="hero-bg-mask" ref={maskRef}></div>

      <div className="hero-content" ref={textGroupRef}>
        <div className="hero-badge">
          <Sparkles size={14} />
          <span>Enterprise Playbook Platform</span>
        </div>
        <h1 className="text-giant hero-title">
          Play Book<br />
          <span className="gradient-text">Studio.</span>
        </h1>
        <p className="text-subtitle hero-subtitle">
          복잡한 매뉴얼을 실행 가능한 지식으로.<br />
          질문하면 답하고, 바로 쓸 수 있는 플레이북을 만듭니다.
        </p>

        <div className="hero-actions">
          <Link to={ROUTES.pbsStudio} className="primary-cta">
            <span>Launch Studio</span>
            <ArrowRight size={18} />
          </Link>
          <Link to={ROUTES.aiOps} className="secondary-cta hero-aiops-cta">
            <span>AI Ops</span>
            <ArrowRight size={18} />
          </Link>
          <button className="secondary-cta" type="button">Demo 영상</button>
        </div>
      </div>

      <div className="hero-scroll-indicator">
        <div className="mouse-icon">
          <div className="mouse-wheel"></div>
        </div>
        <span>Knowledge</span>
      </div>
    </section>
  );
}
