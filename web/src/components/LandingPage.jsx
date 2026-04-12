import React from 'react';
import './LandingPage.css';

function LandingPage({
  brandLogo,
  authMode,
  setAuthMode,
  submitAuth,
  authName,
  setAuthName,
  authEmail,
  setAuthEmail,
  authPassword,
  setAuthPassword,
  authBusy,
  authError,
}) {
  return (
    <div className="landingWrap">
      {/* Dynamic Background Elements */}
      <div className="glow-mesh" />
      
      <nav className="landingNav">
        <div className="navLogo">
          <img src={brandLogo} alt="Logo" />
          <span>RAG<span>Enterprise</span></span>
        </div>
        <div className="navLinks">
          <a href="#features">Security</a>
          <a href="#docs">Documentation</a>
        </div>
      </nav>

      <main className="landingMain">
        <section className="landingHero">
          <div className="heroContent">
            <div className="heroBadge">
              <span className="pulseDot"></span>
              Enterprise Ready
            </div>
            <h1>
              Intelligence <br /> 
              <span className="textGradient">Beyond Retrieval.</span>
            </h1>
            <p className="heroSubtext">
              Secure, private document intelligence powered by hybrid search and 
              source-backed reranking. The bridge between your data and answers.
            </p>
            
            <div className="featureCapsules">
              <div className="capsule">✦ JWT Protected</div>
              <div className="capsule">✦ Hybrid Rerank</div>
              <div className="capsule">✦ FastAPI Core</div>
            </div>
          </div>

          <div className="authContainer">
            <div className="authCard">
              <div className="authHeader">
                <h2>{authMode === 'login' ? 'Welcome Back' : 'Get Started'}</h2>
                <p>Enter your credentials to access the vault.</p>
              </div>

              <div className="authTabs">
                <button 
                  type="button" 
                  className={authMode === 'login' ? 'active' : ''} 
                  onClick={() => setAuthMode('login')}
                >
                  Sign In
                </button>
                <button 
                  type="button" 
                  className={authMode === 'register' ? 'active' : ''} 
                  onClick={() => setAuthMode('register')}
                >
                  Register
                </button>
              </div>

              <form className="authForm" onSubmit={submitAuth}>
                {authMode === 'register' && (
                  <div className="inputGroup">
                    <label>Full Name</label>
                    <input
                      type="text"
                      placeholder="Alex Rivera"
                      value={authName}
                      onChange={(e) => setAuthName(e.target.value)}
                      disabled={authBusy}
                    />
                  </div>
                )}

                <div className="inputGroup">
                  <label>Email Address</label>
                  <input
                    type="email"
                    placeholder="name@company.com"
                    value={authEmail}
                    onChange={(e) => setAuthEmail(e.target.value)}
                    disabled={authBusy}
                    required
                  />
                </div>

                <div className="inputGroup">
                  <label>Password</label>
                  <input
                    type="password"
                    placeholder="••••••••"
                    value={authPassword}
                    onChange={(e) => setAuthPassword(e.target.value)}
                    disabled={authBusy}
                    required
                    minLength={8}
                  />
                </div>

                {authError && <div className="authError">{authError}</div>}

                <button type="submit" className="authSubmit" disabled={authBusy}>
                  {authBusy ? (
                    <span className="loader"></span>
                  ) : (
                    authMode === 'login' ? 'Access Dashboard' : 'Create Account'
                  )}
                </button>
              </form>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

export default LandingPage;