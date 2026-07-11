import React, { useState } from 'react';
import { useSelector } from 'react-redux';
import type { RootState } from '../../store';
import './FormPanel.css';

const INTERACTION_TYPES = ['Meeting', 'Call', 'Email', 'Conference', 'Virtual'];



const FormPanel: React.FC = () => {
  const form = useSelector((state: RootState) => state.form);
  const [voiceToast, setVoiceToast] = useState(false);

  const handleVoiceNote = () => {
    setVoiceToast(true);
    setTimeout(() => setVoiceToast(false), 4000);
  };

  return (
    <div className="form-panel">
      <div className="form-panel__header">
        <h1 className="form-panel__title">Log HCP Interaction</h1>
      </div>

      <div className="form-panel__body">
        <p className="form-section-label">Interaction Details</p>

        {/* Row 1: HCP Name + Interaction Type */}
        <div className="form-row">
          <div className="form-field">
            <label className="form-label">HCP Name</label>
            <div className="form-input-wrapper">
              <input
                type="text"
                className="form-input"
                readOnly
                value={form.hcp_name}
                placeholder="Search or select HCP..."
              />
              {form.hcp_name && (
                <span className="form-input-filled-badge">AI Filled</span>
              )}
            </div>
          </div>

          <div className="form-field">
            <label className="form-label">Interaction Type</label>
            <div className="form-select-wrapper">
              <select
                className="form-select"
                disabled
                value={form.interaction_type}
              >
                {INTERACTION_TYPES.map((t) => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
              <span className="select-arrow">▾</span>
            </div>
          </div>
        </div>

        {/* Row 2: Date + Time */}
        <div className="form-row">
          <div className="form-field">
            <label className="form-label">Date</label>
            <div className="form-input-wrapper">
              <input
                type="date"
                className="form-input"
                readOnly
                value={form.date}
              />
            </div>
          </div>

          <div className="form-field">
            <label className="form-label">Time</label>
            <div className="form-input-wrapper">
              <input
                type="text"
                className="form-input"
                readOnly
                value={form.time}
                placeholder="HH:MM AM/PM"
              />
              <span className="input-icon">⏰</span>
            </div>
          </div>
        </div>

        {/* Sentiment badge */}
        {form.sentiment && (
          <div className="form-field form-field--full">
            <label className="form-label">Observed/Inferred HCP Sentiment</label>
            <div className="sentiment-radio-group">
              {['Positive', 'Neutral', 'Negative'].map((s) => (
                <label key={s} className={`sentiment-radio-option ${form.sentiment === s ? 'sentiment-radio-option--active' : ''}`}>
                  <input type="radio" checked={form.sentiment === s} readOnly disabled />
                  <span className="sentiment-emoji">
                    {s === 'Positive' && '😊'}
                    {s === 'Neutral' && '😐'}
                    {s === 'Negative' && '😞'}
                  </span>
                  {s}
                </label>
              ))}
            </div>
          </div>
        )}

        {/* Attendees */}
        <div className="form-field form-field--full">
          <label className="form-label">Attendees</label>
          <input
            type="text"
            className="form-input"
            readOnly
            value={form.attendees}
            placeholder="Enter names or search..."
          />
        </div>

        {/* Topics Discussed */}
        <div className="form-field form-field--full">
          <label className="form-label">Topics Discussed</label>
          <textarea
            className="form-textarea"
            readOnly
            value={form.topics_discussed}
            placeholder="Enter key discussion points..."
            rows={4}
          />
        </div>

        {/* Voice note link */}
        <div className="voice-note-link" onClick={handleVoiceNote}>
          <span className="voice-note-icon">✏️</span>
          <span>Summarize from Voice Note (Requires Consent)</span>
        </div>

        {/* Voice toast notification */}
        {voiceToast && (
          <div className="voice-toast">
            🎤 Voice note simulation: Please type or dictate your meeting notes in the AI chat on the right panel. The AI will automatically extract all fields.
          </div>
        )}

        {/* MATERIALS SHARED / SAMPLES DISTRIBUTED */}
        <div className="form-section">
          <p className="form-section-label">Materials Shared / Samples Distributed</p>

          {/* Materials Shared */}
          <label className="form-label">Materials Shared</label>
          <div className="materials-box">
            {form.materials_shared.length === 0 ? (
              <span className="materials-empty">No materials added.</span>
            ) : (
              <ul className="materials-list">
                {form.materials_shared.map((m, i) => (
                  <li key={i} className="material-tag">
                    <span className="material-icon">📄</span>
                    {m}
                  </li>
                ))}
              </ul>
            )}
            <div className="materials-footer">
              <button className="btn-search-add" disabled>
                <span>🔍</span> Search/Add
              </button>
            </div>
          </div>

          {/* Samples Distributed */}
          <label className="form-label" style={{ marginTop: '12px' }}>Samples Distributed</label>
          <div className="materials-box">
            {form.samples_distributed.length === 0 ? (
              <span className="materials-empty">No samples added.</span>
            ) : (
              <ul className="materials-list">
                {form.samples_distributed.map((s, i) => (
                  <li key={i} className="material-tag material-tag--sample">
                    <span className="material-icon">💊</span>
                    {s}
                  </li>
                ))}
              </ul>
            )}
            <div className="materials-footer">
              <button className="btn-search-add" disabled>
                <span>+</span> Add Sample
              </button>
            </div>
          </div>
        </div>

        {/* Outcomes */}
        <div className="form-field form-field--full">
          <label className="form-label">Outcomes</label>
          <textarea
            className="form-textarea"
            readOnly
            value={form.outcomes}
            placeholder="Key outcomes or agreements..."
            rows={3}
          />
        </div>

        {/* Follow-up Actions */}
        <div className="form-field form-field--full">
          <label className="form-label">Follow-up Actions</label>
          <textarea
            className="form-textarea"
            readOnly
            value={form.follow_up_actions}
            placeholder="Next steps or follow-up actions..."
            rows={3}
          />
        </div>

        {/* AI Summary */}
        {form.summary && (
          <div className="form-section">
            <label className="form-label">AI Generated Summary</label>
            <div className="summary-box">
              {form.summary}
            </div>
          </div>
        )}

        {/* Read-only notice */}
        <div className="readonly-notice">
          <span className="readonly-icon">🤖</span>
          <span>This form is AI-controlled. Use the assistant on the right to fill or edit fields.</span>
        </div>
      </div>
    </div>
  );
};

export default FormPanel;
