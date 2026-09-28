import React, { useEffect } from 'react';
import { Cpu, Activity, RefreshCw } from 'lucide-react';
import { useSettingsStore } from '../../store/settingsStore';

export const ModelPulseBadge: React.FC = () => {
  const { modelStatus, checkModelPulse, openSettingsModal } = useSettingsStore();

  useEffect(() => {
    // Initial pulse check
    checkModelPulse();
    // Auto-pulse heartbeat every 25 seconds
    const interval = setInterval(() => {
      checkModelPulse();
    }, 25000);
    return () => clearInterval(interval);
  }, [checkModelPulse]);

  const status = modelStatus?.status || 'checking';
  const provider = modelStatus?.provider || 'ollama_cloud';
  const modelName = modelStatus?.model_name || 'llama3.3:70b';
  const latency = modelStatus?.latency_ms;

  const getStatusColor = () => {
    switch (status) {
      case 'online':
        return {
          bg: 'bg-emerald-950/70 border-emerald-800/80 text-emerald-300',
          dot: 'bg-emerald-400',
          ping: 'bg-emerald-500',
        };
      case 'degraded':
        return {
          bg: 'bg-amber-950/70 border-amber-800/80 text-amber-300',
          dot: 'bg-amber-400',
          ping: 'bg-amber-500',
        };
      case 'offline':
        return {
          bg: 'bg-rose-950/70 border-rose-800/80 text-rose-300',
          dot: 'bg-rose-400',
          ping: 'bg-rose-500',
        };
      default:
        return {
          bg: 'bg-slate-900 border-slate-800 text-slate-400',
          dot: 'bg-blue-400',
          ping: 'bg-blue-500',
        };
    }
  };

  const colors = getStatusColor();

  return (
    <button
      onClick={openSettingsModal}
      title={`Live Model: ${modelName} (${provider}) • Status: ${status} • Click to configure`}
      className={`flex items-center space-x-2 px-2.5 py-1 rounded-full border text-xs font-medium transition hover:brightness-110 shadow-sm ${colors.bg}`}
    >
      {/* Animated Heartbeat Pulse Indicator */}
      <span className="relative flex h-2 w-2">
        {status === 'online' && (
          <span
            className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${colors.ping}`}
          />
        )}
        <span className={`relative inline-flex rounded-full h-2 w-2 ${colors.dot}`} />
      </span>

      {/* Model Name & Provider */}
      <div className="flex items-center space-x-1.5 font-mono text-[11px]">
        <Cpu className="w-3.5 h-3.5 opacity-80" />
        <span className="font-semibold text-slate-100 max-w-[120px] truncate">{modelName}</span>
      </div>

      {/* Latency Pill */}
      {latency !== undefined && latency !== null && status !== 'offline' && (
        <span className="text-[10px] px-1.5 py-0.2 rounded bg-black/40 text-slate-300 font-mono">
          {latency}ms
        </span>
      )}
    </button>
  );
};
