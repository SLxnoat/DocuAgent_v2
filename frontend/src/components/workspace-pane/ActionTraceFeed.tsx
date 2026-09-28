import React from 'react';
import { useSessionStore } from '../../store/sessionStore';
import { MousePointer, Type, Navigation, ListOrdered } from 'lucide-react';

export const ActionTraceFeed: React.FC = () => {
  const { actions } = useSessionStore();

  if (actions.length === 0) return null;

  return (
    <div className="h-32 border-t border-slate-800 bg-slate-900/60 flex flex-col shrink-0">
      <div className="h-7 bg-slate-900 px-3 flex items-center justify-between border-b border-slate-800">
        <div className="flex items-center space-x-1.5 text-slate-400">
          <ListOrdered className="w-3.5 h-3.5" />
          <span className="text-[11px] font-bold uppercase tracking-wider">Live Action-Trace Feed</span>
        </div>
        <span className="text-[10px] text-slate-500 font-mono">{actions.length} recorded</span>
      </div>

      <div className="flex-1 overflow-x-auto p-2 flex items-center space-x-2">
        {actions.map((act) => (
          <div
            key={act.id}
            className="flex-shrink-0 w-60 h-20 bg-slate-950 border border-slate-800 rounded-lg p-2 flex flex-col justify-between hover:border-slate-700 transition text-[11px]"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-1 text-blue-400 font-semibold">
                {act.action_type === 'click' ? (
                  <MousePointer className="w-3 h-3" />
                ) : act.action_type === 'navigation' ? (
                  <Navigation className="w-3 h-3 text-emerald-400" />
                ) : (
                  <Type className="w-3 h-3 text-purple-400" />
                )}
                <span className="capitalize">{act.action_type}</span>
              </div>
              <span className="text-[9px] text-slate-500 font-mono">#{act.sequence_number}</span>
            </div>

            <div className="truncate text-slate-300">
              {act.target_element?.inner_text ||
                act.input_value ||
                act.target_element?.css_selector ||
                act.page_title}
            </div>

            <div className="text-[9px] text-slate-500 truncate font-mono">
              {act.target_element?.tag_name || 'page'}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
