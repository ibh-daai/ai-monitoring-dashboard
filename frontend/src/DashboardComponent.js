import React, { useEffect, useRef } from 'react';

const DashboardComponent = ({ url }) => {
  const iframeRef = useRef(null);

  useEffect(() => {
    const iframe = iframeRef.current;
    if (iframe) {
      iframe.src = url;
    }
  }, [url]);

  return (
    <iframe 
      id="evidently-iframe"
      ref={iframeRef}
      src={url}
      style={{ 
        width: '100%', 
        height: '100%', 
        border: 'none',
        position: 'absolute',
        top: 0,
        left: 0,
      }} 
      title="Evidently Dashboard"
    />
  );
};

export default DashboardComponent;
