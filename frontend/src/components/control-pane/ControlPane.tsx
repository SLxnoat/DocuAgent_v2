import React, { useState } from 'react';
import { UrlConfigCard } from './UrlConfigCard';
import { AuthCredentialsCard } from './AuthCredentialsCard';
import { RecordingControls } from './RecordingControls';
import { ExportActionCard } from './ExportActionCard';
import { AuthCredentials } from '../../types/session';
import { useSessionStore } from '../../store/sessionStore';
import { sessionsApi } from '../../api/sessions';

export const ControlPane: React.FC = () => {
  const [url, setUrl] = useState('https://example.com');
  const [title, setTitle] = useState('Example Workflow Guide');
  const [credentials, setCredentials] = useState<AuthCredentials>({ auth_type: 'none' });
  const [isLoading, setIsLoading] = useState(false);

  const { isRecording, setCurrentSession, resetSession } = useSessionStore();

  const handleStartSession = async () => {
    setIsLoading(true);
    resetSession();
    try {
      const sess = await sessionsApi.createSession({
        target_url: url,
        title,
        credentials: credentials.username ? credentials : undefined,
      });
      setCurrentSession(sess);
    } catch (err) {
      console.error('Failed to start session:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-4 space-y-4">
      <div className="pb-1 border-b border-slate-800">
        <h2 className="text-sm font-bold text-white tracking-tight">Control Panel</h2>
        <p className="text-[11px] text-slate-400">Configure recording target & export output</p>
      </div>

      <UrlConfigCard
        url={url}
        setUrl={setUrl}
        title={title}
        setTitle={setTitle}
        disabled={isRecording}
      />

      <AuthCredentialsCard
        credentials={credentials}
        setCredentials={setCredentials}
        disabled={isRecording}
      />

      <RecordingControls
        url={url}
        title={title}
        onStartSession={handleStartSession}
        isLoading={isLoading}
      />

      <ExportActionCard />
    </div>
  );
};
