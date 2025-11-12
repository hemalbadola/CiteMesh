import { lazy, Suspense, useCallback, useEffect, useRef, useState } from 'react'
import './App.css'
import PaperVerseLoader from './components/PaperVerseLoader'

const SceneManager = lazy(() => import('./components/SceneManager'))

declare global {
  interface Window {
    PAPERVERSE_BACKEND?: string
  }
}

function App() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const mainRef = useRef<HTMLElement | null>(null)

  const [sceneReady, setSceneReady] = useState(false)
  const [loaderVisible, setLoaderVisible] = useState(true)
  const [loaderExiting, setLoaderExiting] = useState(false)
  const [scrollProgress, setScrollProgress] = useState(0)
  const [showBackToTop, setShowBackToTop] = useState(false)

  const loaderExitTimeout = useRef<number | undefined>(undefined)
  const loaderTriggeredRef = useRef(false)

  useEffect(() => {
    return () => {
      if (loaderExitTimeout.current !== undefined) {
        window.clearTimeout(loaderExitTimeout.current)
      }
    }
  }, [])

  // Track scroll progress
  useEffect(() => {
    const handleScroll = () => {
      const windowHeight = window.innerHeight
      const documentHeight = document.documentElement.scrollHeight
      const scrollTop = window.scrollY
      const scrollableHeight = documentHeight - windowHeight
      const progress = scrollableHeight > 0 ? (scrollTop / scrollableHeight) * 100 : 0
      
      setScrollProgress(progress)
      setShowBackToTop(scrollTop > windowHeight)
    }

    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handleSceneReady = useCallback(() => {
    if (loaderTriggeredRef.current) return
    loaderTriggeredRef.current = true
    setSceneReady(true)
    setLoaderExiting(true)
    loaderExitTimeout.current = window.setTimeout(() => setLoaderVisible(false), 650)
  }, [])

  return (
    <>
      {loaderVisible && (
        <PaperVerseLoader
          fullscreen
          isExiting={loaderExiting}
          message={sceneReady ? 'PaperVerse is ready to explore.' : 'Folding the PaperVerse lattice…'}
        />
      )}

      {/* Login Button */}
      <a
        href="/login"
        className="fixed top-6 right-6 z-50 bg-purple-600/80 backdrop-blur-md hover:bg-purple-500 text-white font-semibold px-6 py-3 rounded-full shadow-lg transition-all duration-300 hover:scale-105 hover:shadow-purple-500/50 border border-purple-400/20"
      >
        Sign In
      </a>

      {/* Scroll Progress Bar */}
      <div className="fixed top-0 left-0 w-full h-1 bg-transparent z-50 pointer-events-none">
        <div
          className="h-full bg-gradient-to-r from-purple-600 via-purple-500 to-purple-400 transition-all duration-300 ease-out"
          style={{ width: `${scrollProgress}%` }}
        />
      </div>

      {/* Back to Top Button */}
      {showBackToTop && (
        <button
          onClick={scrollToTop}
          className="fixed bottom-8 right-8 z-50 bg-purple-600 hover:bg-purple-500 text-white p-4 rounded-full shadow-lg transition-all duration-300 hover:scale-110 hover:shadow-purple-500/50"
          aria-label="Back to top"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M5 10l7-7m0 0l7 7m-7-7v18" />
          </svg>
        </button>
      )}

      <div id="smooth-wrapper">
        <div id="smooth-content">
          <Suspense fallback={<PaperVerseLoader fullscreen message="Rendering PaperVerse constellation…" />}>
            <SceneManager canvasRef={canvasRef} mainRef={mainRef} onReady={handleSceneReady} />
          </Suspense>
          <main ref={mainRef} className="relative z-10">
          <section id="section-1" className="content-section section-1">
            <h1 className="text-4xl md:text-7xl font-black uppercase tracking-wider text-white mb-4">
              PaperVerse <span className="text-purple-500">Research Intelligence</span>
            </h1>
            <p className="text-lg md:text-xl text-slate-300 max-w-3xl mx-auto mb-8">
              A living knowledge engine that turns open scholarly data into daily, citation-aware briefings for
              universities and research teams.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a href="#section-2" className="cta-button bg-purple-600 text-white font-bold py-3 px-8 rounded-full text-lg">
                Explore the Platform
              </a>
              <a
                href="#section-4"
                className="secondary-button border-2 border-slate-500 text-slate-300 font-bold py-3 px-8 rounded-full text-lg text-center"
              >
                View Sample Brief
              </a>
            </div>
          </section>

          <section id="section-2" className="content-section section-2">
            <div className="glass-panel max-w-lg">
              <h2 className="text-3xl md:text-5xl font-bold text-white mb-6">Discovery Shouldn't Drain Your Research Hours.</h2>
              <ul className="space-y-4 text-slate-300 text-lg">
                <li className="pain-point opacity-0">Scattered repositories, publishers, and APIs to reconcile.</li>
                <li className="pain-point opacity-0">Opaque citation signals that obscure genuine influence.</li>
                <li className="pain-point opacity-0">Open-access policies changing faster than your literature reviews.</li>
              </ul>
            </div>
          </section>

          <section id="section-3" className="content-section">
            <div id="card-observe" className="glass-panel process-card">
              <h2 className="text-3xl font-bold text-white mb-2">We Ingest.</h2>
              <p className="text-slate-300">
                PaperVerse syncs live from OpenAlex, arXiv, and institutional feeds, mapping every new paper to your
                research landscape.
              </p>
            </div>
            <div id="card-orient" className="glass-panel process-card ml-auto text-right">
              <h2 className="text-3xl font-bold text-white mb-2">We Understand.</h2>
              <p className="text-slate-300">
                Gemini-powered translation aligns plain-language questions with citation filters, institutions, and
                concept taxonomies.
              </p>
            </div>
            <div id="card-decide" className="glass-panel process-card">
              <h2 className="text-3xl font-bold text-white mb-2">We Synthesize.</h2>
              <p className="text-slate-300">
                Our pipeline ranks by impact, aggregates open-access routes, and flags collaborations you might be
                missing.
              </p>
            </div>
            <div id="card-act" className="glass-panel process-card ml-auto text-right">
              <h2 className="text-3xl font-bold text-white mb-2">So You Can Lead.</h2>
              <p className="text-slate-300">
                Daily intelligence briefs, citation dashboards, and inline PDFs keep your teams ahead of funding calls
                and publication waves.
              </p>
            </div>
          </section>

          <section id="section-4" className="content-section section-4 flex items-center justify-center">
            <div id="solution-panel" className="glass-panel w-full max-w-4xl text-left">
              <div className="p-2 md:p-4">
                <div className="flex items-center justify-between border-b border-slate-700/50 pb-4 mb-4">
                  <div className="flex items-center gap-3">
                    <svg
                      className="h-6 w-6 text-purple-500"
                      xmlns="http://www.w3.org/2000/svg"
                      width="24"
                      height="24"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <path d="M4 18.5a2.5 2.5 0 1 0 5 0a2.5 2.5 0 1 0-5 0Z" />
                      <path d="M15 3.5a2.5 2.5 0 1 0 5 0a2.5 2.5 0 1 0-5 0Z" />
                      <path d="M6.5 18.5 17.5 3.5" />
                    </svg>
                    <h2 className="text-2xl md:text-4xl font-bold text-white">PaperVerse Morning Signal</h2>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-semibold text-slate-300">Scholarly Intelligence Desk</p>
                    <p className="text-xs text-slate-400">14 Oct 2025</p>
                  </div>
                </div>

                <p className="font-bold text-purple-500 mb-2 text-sm uppercase tracking-wider">Featured Breakthrough</p>
                <h3 className="text-3xl font-bold text-white mb-6">Reinforcement Learning Systems Now Outperform Classical Planning</h3>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                  <div>
                    <p className="text-sm font-semibold text-slate-400 mb-1">Institution Lead</p>
                    <p className="text-lg text-slate-200">University of Cambridge AI Lab</p>
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-slate-400 mb-1">Citation Velocity</p>
                    <p className="text-lg text-slate-200">+218 cites last 90 days</p>
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-slate-400 mb-1">Open Access</p>
                    <p className="text-lg text-slate-200">Green (arXiv, HAL)</p>
                  </div>
                </div>

                <div className="bg-slate-800/50 rounded-lg p-4 flex items-start gap-4 mb-6">
                  <svg
                    className="h-5 w-5 text-purple-500 mt-1 flex-shrink-0"
                    xmlns="http://www.w3.org/2000/svg"
                    width="24"
                    height="24"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z" />
                    <path d="m9 12 2 2 4-4" />
                  </svg>
                  <div>
                    <h4 className="font-bold text-white">Action Recommended</h4>
                    <p className="text-slate-300 text-sm">
                      Schedule a briefing with the robotics faculty to discuss co-authoring the companion benchmark.
                      PaperVerse preloads annotated datasets and policy diffs.
                    </p>
                  </div>
                </div>

                <div className="text-center">
                  <a
                    href="/login"
                    className="inline-block bg-purple-600 text-white font-bold py-3 px-8 rounded-lg transition-all duration-300 hover:bg-purple-700 hover:scale-105"
                  >
                    Sign In to Launch Console &rarr;
                  </a>
                </div>
              </div>
            </div>
          </section>

          <section id="section-4b" className="content-section section-4">
            <div className="w-full">
              <h2 className="text-3xl md:text-5xl font-bold text-white mb-8 text-center">Why Researchers Trust PaperVerse.</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div className="glass-panel">
                  <h3 className="text-2xl font-bold text-white mb-2">Unified Discovery Mesh</h3>
                  <p className="text-slate-300">
                    Federates OpenAlex, arXiv, and institutional repositories into a citation-normalized knowledge graph
                    updated hourly.
                  </p>
                </div>
                <div className="glass-panel">
                  <h3 className="text-2xl font-bold text-white mb-2">Gemini-Guided Routing</h3>
                  <p className="text-slate-300">
                    Transforms plain-language questions into precise filters, preserving researcher intent while
                    removing manual syntax tweaks.
                  </p>
                </div>
                <div className="glass-panel">
                  <h3 className="text-2xl font-bold text-white mb-2">Embedded Open Access</h3>
                  <p className="text-slate-300">
                    Caches verified OA PDFs through our secure proxy so faculty never leave the portal to read or
                    annotate groundbreaking work.
                  </p>
                </div>
              </div>
            </div>
          </section>

          <section id="section-console" className="content-section section-4">
            <div className="console-card w-full max-w-5xl mx-auto">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div>
                  <p className="tag mb-3">Available in Dashboard</p>
                  <h2 className="text-3xl md:text-4xl font-bold text-white">Ask PaperVerse Anything</h2>
                  <p className="text-slate-300 mt-2 max-w-xl">
                    The live PaperVerse console now lives inside your authenticated dashboard. Sign in to launch natural-language
                    research queries, translate intent, and pull open-access links without leaving your workspace.
                  </p>
                </div>
                <div className="status-indicator status-success">
                  <span className="status-text">Dashboard exclusive &mdash; sign in to access.</span>
                </div>
              </div>

              <div className="flex flex-col sm:flex-row gap-3 justify-end mt-8">
                <a
                  href="/login"
                  className="cta-button bg-purple-600 text-white font-bold py-3 px-8 rounded-lg text-center"
                >
                  Sign In to Use Console
                </a>
                <a
                  href="/dashboard"
                  className="secondary-button border-2 border-slate-600 text-slate-300 font-medium py-3 px-6 rounded-lg text-center"
                >
                  Go to Dashboard
                </a>
              </div>
            </div>
          </section>

          <section id="section-5" className="content-section section-5">
            <div className="w-full">
              <h2 className="text-3xl md:text-5xl font-bold text-white mb-8 text-center">Impact Across Campuses & Labs.</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div className="glass-panel text-center">
                  <h3 className="impact-number text-purple-500 text-4xl font-bold mb-2">88%</h3>
                  <p className="text-lg font-semibold text-white">Faster Literature Scans</p>
                  <p className="text-slate-400 mt-1">Graduate Research Cohorts</p>
                </div>
                <div className="glass-panel text-center">
                  <h3 className="impact-number text-purple-500 text-4xl font-bold mb-2">4.2x</h3>
                  <p className="text-lg font-semibold text-white">Increase in High-Impact Collaborations</p>
                  <p className="text-slate-400 mt-1">Institutional Partnerships</p>
                </div>
                <div className="glass-panel text-center">
                  <h3 className="impact-number text-purple-500 text-4xl font-bold mb-2">97%</h3>
                  <p className="text-lg font-semibold text-white">OA Access Within PaperVerse</p>
                  <p className="text-slate-400 mt-1">Faculty Reading Sessions</p>
                </div>
              </div>
            </div>
          </section>

          <section id="section-6" className="content-section section-6">
            <h2 id="orchestrate-heading" className="text-4xl md:text-6xl font-black text-white mb-4">
              Ready to <span className="heading-word">Orchestrate</span> Your <span className="heading-word">Institution's</span> <span className="text-purple-500">Research Edge?</span>
            </h2>
            <p className="text-slate-300 text-lg max-w-2xl mx-auto mb-8">
              Book a strategic session with the PaperVerse team to tailor daily intelligence feeds, citation dashboards,
              and OA access for your faculty network.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href="/login"
                className="cta-button bg-purple-600 text-white font-bold py-3 px-8 rounded-full text-lg text-center"
              >
                Sign In for Live Console
              </a>
              <a
                href="mailto:intel@paperverse.ai"
                className="secondary-button border-2 border-slate-500 text-slate-300 font-bold py-3 px-8 rounded-full text-lg text-center"
              >
                Contact Intelligence Desk
              </a>
            </div>
          </section>
          </main>
        </div>
      </div>
    </>
  )
}

export default App
