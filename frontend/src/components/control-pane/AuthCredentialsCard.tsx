import React, { useState } from 'react';
import { KeyRound, ChevronDown, ChevronUp } from 'lucide-react';
import { AuthCredentials } from '../../types/session';

interface AuthCredentialsCardProps {
  credentials: AuthCredentials;
  setCredentials: (creds: AuthCredentials) => void;
  disabled?: boolean;
}

export const AuthCredentialsCard: React.FC<AuthCredentialsCardProps> = ({
  credentials,
  setCredentials,
  disabled = false,
}) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 shadow-sm">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between text-left focus:outline-none"
      >
        <div className="flex items-center space-x-2">
          <KeyRound className="w-4 h-4 text-amber-400" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">Auth Credentials</h3>
        </div>
        {isOpen ? <ChevronUp className="w-4 h-4 text-slate-500" /> : <ChevronDown className="w-4 h-4 text-slate-500" />}
      </button>

      {isOpen && (
        <div className="mt-3 space-y-2.5 pt-2 border-t border-slate-800/80">
          <div>
            <label className="block text-[11px] font-medium text-slate-400 mb-1">Username / Email</label>
            <input
              type="text"
              value={credentials.username || ''}
              onChange={(e) => setCredentials({ ...credentials, username: e.target.value })}
              disabled={disabled}
              placeholder="admin@example.com"
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 transition disabled:opacity-50"
            />
          </div>

          <div>
            <label className="block text-[11px] font-medium text-slate-400 mb-1">Password</label>
            <input
              type="password"
              value={credentials.password || ''}
              onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
              disabled={disabled}
              placeholder="••••••••••••"
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 transition disabled:opacity-50"
            />
          </div>
        </div>
      )}
    </div>
  );
};
