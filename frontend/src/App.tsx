import React, { useState } from 'react';
import { Provider } from 'react-redux';
import { store } from './store';
import FormPanel from './components/FormPanel/FormPanel';
import ChatPanel from './components/ChatPanel/ChatPanel';
import './App.css';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState('log');
  const [toast, setToast] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(null), 3500);
  };

  const handleNavClick = (tab: string) => {
    if (tab === 'log') {
      setActiveTab('log');
    } else if (tab === 'hcp') {
      setActiveTab('hcp');
      showToast('📋 HCP Directory: Displays a searchable list of all healthcare professionals. Feature coming soon.');
    } else if (tab === 'reports') {
      setActiveTab('reports');
      showToast('📊 Reports: Interaction analytics, sentiment trends, and coverage dashboards. Feature coming soon.');
    }
  };

  return (
    <Provider store={store}>
      <div className="app-root">
        {/* Top navigation bar */}
        <header className="app-nav">
          <div className="app-nav__brand">
            <span className="brand-icon">💊</span>
            <span className="brand-name">PharmaCRM</span>
            <span className="brand-badge">HCP Module</span>
          </div>
          <nav className="app-nav__links">
            <a
              href="#"
              className={`nav-link ${activeTab === 'log' ? 'nav-link--active' : ''}`}
              onClick={(e) => { e.preventDefault(); handleNavClick('log'); }}
            >
              Log Interaction
            </a>
            <a
              href="#"
              className={`nav-link ${activeTab === 'hcp' ? 'nav-link--active' : ''}`}
              onClick={(e) => { e.preventDefault(); handleNavClick('hcp'); }}
            >
              HCP Directory
            </a>
            <a
              href="#"
              className={`nav-link ${activeTab === 'reports' ? 'nav-link--active' : ''}`}
              onClick={(e) => { e.preventDefault(); handleNavClick('reports'); }}
            >
              Reports
            </a>
          </nav>
          <div className="app-nav__user">
            <div className="user-avatar">JS</div>
            <span className="user-name">Sales Rep</span>
          </div>
        </header>

        {/* Toast notification */}
        {toast && (
          <div className="app-toast">
            {toast}
          </div>
        )}

        {/* Main split-screen layout */}
        <main className="app-main">
          {/* Left: Form Panel */}
          <div className="panel panel--form">
            <FormPanel />
          </div>

          {/* Divider */}
          <div className="panel-divider" />

          {/* Right: Chat Panel */}
          <div className="panel panel--chat">
            <ChatPanel />
          </div>
        </main>
      </div>
    </Provider>
  );
};

export default App;
