import React from 'react';
import { Provider } from 'react-redux';
import { store } from './store';
import FormPanel from './components/FormPanel/FormPanel';
import ChatPanel from './components/ChatPanel/ChatPanel';
import './App.css';

const App: React.FC = () => {
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
            <a href="#" className="nav-link nav-link--active">Log Interaction</a>
            <a href="#" className="nav-link">HCP Directory</a>
            <a href="#" className="nav-link">Reports</a>
          </nav>
          <div className="app-nav__user">
            <div className="user-avatar">JS</div>
            <span className="user-name">Sales Rep</span>
          </div>
        </header>

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
