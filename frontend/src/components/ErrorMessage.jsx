import React from 'react';

const ErrorMessage = ({ message, onDismiss }) => {
  return (
    <div className="error-message">
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <span style={{ marginRight: '8px' }}>❌</span>
        <span>{message}</span>
        {onDismiss && (
          <button
            onClick={onDismiss}
            style={{
              marginLeft: 'auto',
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              fontSize: '18px',
            }}
          >
            &times;
          </button>
        )}
      </div>
    </div>
  );
};

export default ErrorMessage; 