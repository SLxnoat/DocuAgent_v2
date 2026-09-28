import React, { useState } from 'react';
import { Globe, Link2 } from 'lucide-react';

interface UrlConfigCardProps {
  url: string;
  setUrl: (url: string) => void;
  title: string;
  setTitle: (title: string) => void;
  disabled?: boolean;
}

export const UrlConfigCard: React.FC<UrlConfigCardProps> = ({
  url,
  setUrl,
  title,
  setTitle,
  disabled = false,
}) => {
  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 shadow-sm">
      <div className="flex items-center space-x-2 mb-3">
        <Globe className="w-4 h-4 text-blue-400" />
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">Target Application</h3>
      </div>

      <div className="space-y-3">
        <div>
          <label className="block text-xs font-medium text-slate-400 mb-1">Workflow Title</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            disabled={disabled}
            placeholder="e.g. Generating Customer Invoice"
            className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 transition disabled:opacity-50"
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-400 mb-1">Starting URL</label>
          <div className="relative">
            <Link2 className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-2.5" />
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              disabled={disabled}
              placeholder="https://app.example.com"
              className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 transition disabled:opacity-50"
            />
          </div>
        </div>
      </div>
    </div>
  );
};
