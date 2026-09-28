import React, { useState, useEffect } from 'react';
import {
  X,
  Cpu,
  Sliders,
  Palette,
  FileDown,
  CheckCircle2,
  AlertCircle,
  Loader2,
  RefreshCw,
  Sparkles,
  Zap,
} from 'lucide-react';
import { useSettingsStore } from '../../store/settingsStore';
import { settingsApi } from '../../api/settings';
import { LLMProvider, ModelTestResponse } from '../../types/settings';

export const SettingsModal: React.FC = () => {
  const {
    settings,
    isSettingsModalOpen,
    closeSettingsModal,
    fetchSettings,
    updateSettings,
    checkModelPulse,
  } = useSettingsStore();

  const [activeTab, setActiveTab] = useState<'model' | 'browser' | 'export'>('model');

  // Form State
  const [provider, setProvider] = useState<LLMProvider>('ollama_cloud');
  const [baseUrl, setBaseUrl] = useState('https://ollama.com/api');
  const [apiKey, setApiKey] = useState('');
  const [defaultModel, setDefaultModel] = useState('llama3.3:70b');
  const [fastModel, setFastModel] = useState('llama3.1:8b');

  // Browser state
  const [highlightColor, setHighlightColor] = useState('#ef4444');
  const [viewportWidth, setViewportWidth] = useState(1440);
  const [viewportHeight, setViewportHeight] = useState(900);
  const [screencastFps, setScreencastFps] = useState(15);
  const [screencastQuality, setScreencastQuality] = useState(80);

  // Test Connection State
  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState<ModelTestResponse | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [discoveredModels, setDiscoveredModels] = useState<string[]>([]);
  const [isLoadingModels, setIsLoadingModels] = useState(false);

  const fetchModels = async () => {
    setIsLoadingModels(true);
    try {
      const res = await settingsApi.getAvailableModels();
      if (res.success && res.models.length > 0) {
        setDiscoveredModels(res.models);
        // Auto-select the first model if none selected or current not in list
        setDefaultModel((prev) =>
          res.models.includes(prev) ? prev : res.models[0]
        );
      }
    } finally {
      setIsLoadingModels(false);
    }
  };

  useEffect(() => {
    if (isSettingsModalOpen) {
      fetchSettings();
      fetchModels();
    }
  }, [isSettingsModalOpen, fetchSettings]);

  useEffect(() => {
    if (settings) {
      setProvider(settings.llm_provider);
      setBaseUrl(settings.ollama_base_url);
      setDefaultModel(settings.default_model);
      setFastModel(settings.fast_model);
      setHighlightColor(settings.highlight_color);
      setViewportWidth(settings.viewport_width);
      setViewportHeight(settings.viewport_height);
      setScreencastFps(settings.screencast_fps);
      setScreencastQuality(settings.screencast_quality);
    }
  }, [settings]);

  const handleTestConnection = async () => {
    setIsTesting(true);
    setTestResult(null);
    try {
      const res = await settingsApi.testModelConnection({
        provider,
        base_url: baseUrl,
        api_key: apiKey || undefined,
        model_name: defaultModel,
      });
      setTestResult(res);
    } catch (err: any) {
      setTestResult({
        success: false,
        latency_ms: 0,
        provider,
        model_name: defaultModel,
        error_message: err.message || 'Connection test failed',
      });
    } finally {
      setIsTesting(false);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    setSaveSuccess(false);
    try {
      // Resolve API key:
      //  - '\x00clear' sentinel → send "" to backend (clears key in .env)
      //  - empty string       → send undefined (preserve existing key)
      //  - any other value    → send as-is (new key)
      const resolvedApiKey = apiKey === '\x00clear' ? '' : apiKey || undefined;

      await updateSettings({
        llm_provider: provider,
        ollama_base_url: baseUrl,
        ollama_api_key: resolvedApiKey,
        default_model: defaultModel,
        fast_model: fastModel,
        highlight_color: highlightColor,
        viewport_width: viewportWidth,
        viewport_height: viewportHeight,
        screencast_fps: screencastFps,
        screencast_quality: screencastQuality,
      });
      setSaveSuccess(true);
      // Reset apiKey field after successful save
      setApiKey('');
      setTimeout(() => setSaveSuccess(false), 2500);
    } catch (err) {
      console.error('Save settings error:', err);
    } finally {
      setIsSaving(false);
    }
  };

  if (!isSettingsModalOpen) return null;

  const colorPresets = [
    { label: 'Red (Default)', value: '#ef4444' },
    { label: 'Blue', value: '#3b82f6' },
    { label: 'Emerald', value: '#10b981' },
    { label: 'Purple', value: '#8b5cf6' },
    { label: 'Amber', value: '#f59e0b' },
    { label: 'Cyan', value: '#06b6d4' },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4 animate-in fade-in duration-150">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-2xl overflow-hidden shadow-2xl flex flex-col max-h-[90vh]">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-blue-600/20 border border-blue-500/40 flex items-center justify-center text-blue-400">
              <Sliders className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-white">System Settings & Live Integrator</h2>
              <p className="text-[11px] text-slate-400">Configure LLM providers, model engine, and recording behavior</p>
            </div>
          </div>
          <button
            onClick={closeSettingsModal}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-slate-800 bg-slate-950/40 px-6 pt-2 space-x-4 text-xs font-medium">
          <button
            onClick={() => setActiveTab('model')}
            className={`pb-2.5 flex items-center space-x-2 border-b-2 transition ${
              activeTab === 'model'
                ? 'border-blue-500 text-blue-400 font-semibold'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Cpu className="w-3.5 h-3.5" />
            <span>LLM & Model Engine</span>
          </button>
          <button
            onClick={() => setActiveTab('browser')}
            className={`pb-2.5 flex items-center space-x-2 border-b-2 transition ${
              activeTab === 'browser'
                ? 'border-blue-500 text-blue-400 font-semibold'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Palette className="w-3.5 h-3.5" />
            <span>Browser & Visual Canvas</span>
          </button>
          <button
            onClick={() => setActiveTab('export')}
            className={`pb-2.5 flex items-center space-x-2 border-b-2 transition ${
              activeTab === 'export'
                ? 'border-blue-500 text-blue-400 font-semibold'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <FileDown className="w-3.5 h-3.5" />
            <span>Storage & Export Defaults</span>
          </button>
        </div>

        {/* Tab Contents */}
        <div className="p-6 overflow-y-auto flex-1 space-y-4 text-xs">
          {activeTab === 'model' && (
            <div className="space-y-4">
              {/* Provider Selection */}
              <div>
                <label className="block text-slate-300 font-semibold mb-1.5">LLM Provider</label>
                <select
                  value={provider}
                  onChange={(e) => setProvider(e.target.value as LLMProvider)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="ollama_cloud">Ollama Cloud (Recommended)</option>
                  <option value="ollama_local">Ollama Local</option>
                  <option value="openai">OpenAI (GPT-4o)</option>
                  <option value="litellm">LiteLLM Proxy</option>
                </select>
              </div>

              {/* Base URL */}
              <div>
                <label className="block text-slate-300 font-semibold mb-1.5">Provider Base URL</label>
                <input
                  type="text"
                  value={baseUrl}
                  onChange={(e) => setBaseUrl(e.target.value)}
                  placeholder="https://ollama.com/api or http://localhost:11434"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500 font-mono"
                />
              </div>

              {/* API Key */}
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="text-slate-300 font-semibold">
                    API Key{' '}
                    <span className="text-slate-500 font-normal">(Leave blank to keep existing)</span>
                  </label>
                  {settings?.ollama_api_key_masked && apiKey === '' && (
                    <button
                      type="button"
                      onClick={() => setApiKey('\x00clear')}
                      className="text-[10px] px-2 py-0.5 rounded border border-rose-800 bg-rose-950/40 text-rose-400 hover:text-rose-300 transition"
                    >
                      Clear Key
                    </button>
                  )}
                  {apiKey === '\x00clear' && (
                    <span className="text-[10px] text-rose-400 font-semibold">Key will be cleared on save</span>
                  )}
                </div>
                <input
                  type="password"
                  value={apiKey === '\x00clear' ? '' : apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder={settings?.ollama_api_key_masked || 'No API key set (Ollama local does not require one)'}
                  className={`w-full bg-slate-950 border rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500 font-mono ${
                    apiKey === '\x00clear' ? 'border-rose-700' : 'border-slate-800'
                  }`}
                />
              </div>

              {/* Default Model */}
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="text-slate-300 font-semibold">
                    Synthesis Model{' '}
                    <span className="text-slate-500 font-normal">(Technical Writer / Multi-Agent)</span>
                  </label>
                  <button
                    type="button"
                    onClick={fetchModels}
                    disabled={isLoadingModels}
                    title="Refresh model list from Ollama"
                    className="flex items-center space-x-1 px-2 py-1 rounded-lg border border-slate-700 bg-slate-800 hover:bg-slate-700 text-slate-300 text-[10px] transition disabled:opacity-50"
                  >
                    <RefreshCw className={`w-3 h-3 ${isLoadingModels ? 'animate-spin text-blue-400' : ''}`} />
                    <span>{isLoadingModels ? 'Fetching…' : 'Refresh Models'}</span>
                  </button>
                </div>

                {discoveredModels.length > 0 ? (
                  <select
                    value={defaultModel}
                    onChange={(e) => setDefaultModel(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white font-mono focus:outline-none focus:border-blue-500 cursor-pointer"
                  >
                    {discoveredModels.map((m) => (
                      <option key={m} value={m}>
                        {m}
                      </option>
                    ))}
                  </select>
                ) : (
                  <div className="flex items-center space-x-2 w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-500 font-mono">
                    {isLoadingModels ? (
                      <>
                        <Loader2 className="w-3.5 h-3.5 animate-spin text-blue-400" />
                        <span>Fetching models from Ollama…</span>
                      </>
                    ) : (
                      <span>No models found — check Ollama connection and click Refresh</span>
                    )}
                  </div>
                )}

                {/* Currently selected model badge */}
                {defaultModel && discoveredModels.length > 0 && (
                  <p className="mt-1.5 text-[10px] text-emerald-400 font-mono">
                    ✓ Active model: <span className="font-bold">{defaultModel}</span>
                  </p>
                )}
              </div>

              {/* Fast Model (Speed-optimised tasks) */}
              <div>
                <label className="block text-slate-300 font-semibold mb-1.5">
                  Fast Model{' '}
                  <span className="text-slate-500 font-normal">(Screenshot OCR / Quick classify)</span>
                </label>
                {discoveredModels.length > 0 ? (
                  <select
                    value={fastModel}
                    onChange={(e) => setFastModel(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white font-mono focus:outline-none focus:border-blue-500 cursor-pointer"
                  >
                    {discoveredModels.map((m) => (
                      <option key={m} value={m}>
                        {m}
                      </option>
                    ))}
                  </select>
                ) : (
                  <div className="flex items-center space-x-2 w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-500 font-mono">
                    <span>{isLoadingModels ? 'Fetching…' : 'No models — refresh above'}</span>
                  </div>
                )}
              </div>

              {/* Test Connection Button & Result */}
              <div className="pt-2 border-t border-slate-800/80">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-slate-400 text-xs">Live Integrator Check:</span>
                  <button
                    onClick={handleTestConnection}
                    disabled={isTesting}
                    className="flex items-center space-x-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 px-3 py-1.5 rounded-lg text-xs font-medium transition disabled:opacity-50"
                  >
                    {isTesting ? (
                      <>
                        <Loader2 className="w-3.5 h-3.5 animate-spin text-blue-400" />
                        <span>Pinging Model...</span>
                      </>
                    ) : (
                      <>
                        <Zap className="w-3.5 h-3.5 text-amber-400" />
                        <span>Test Connection</span>
                      </>
                    )}
                  </button>
                </div>

                {testResult && (
                  <div
                    className={`p-3 rounded-xl border text-xs ${
                      testResult.success
                        ? 'bg-emerald-950/40 border-emerald-800 text-emerald-300'
                        : 'bg-rose-950/40 border-rose-800 text-rose-300'
                    }`}
                  >
                    <div className="flex items-center justify-between font-semibold mb-1">
                      <div className="flex items-center space-x-1.5">
                        {testResult.success ? (
                          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                        ) : (
                          <AlertCircle className="w-4 h-4 text-rose-400" />
                        )}
                        <span>{testResult.success ? 'Integrator Online & Responsive' : 'Connection Failed'}</span>
                      </div>
                      {testResult.latency_ms > 0 && (
                        <span className="font-mono text-[11px]">{testResult.latency_ms} ms</span>
                      )}
                    </div>
                    {testResult.sample_response && (
                      <p className="text-[11px] text-slate-300 mt-1 font-mono bg-black/30 p-2 rounded">
                        {testResult.sample_response}
                      </p>
                    )}
                    {testResult.error_message && (
                      <p className="text-[11px] text-rose-300 mt-1">{testResult.error_message}</p>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'browser' && (
            <div className="space-y-4">
              {/* Highlight Color */}
              <div>
                <label className="block text-slate-300 font-semibold mb-1.5">
                  Dynamic UI Highlight Color (Active Element Outline)
                </label>
                <div className="flex items-center space-x-3 mb-2">
                  <input
                    type="color"
                    value={highlightColor}
                    onChange={(e) => setHighlightColor(e.target.value)}
                    className="w-10 h-8 rounded border border-slate-800 bg-slate-950 cursor-pointer"
                  />
                  <input
                    type="text"
                    value={highlightColor}
                    onChange={(e) => setHighlightColor(e.target.value)}
                    className="w-28 bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1 text-xs text-white font-mono"
                  />
                </div>

                <div className="flex items-center gap-2">
                  {colorPresets.map((c) => (
                    <button
                      key={c.value}
                      type="button"
                      onClick={() => setHighlightColor(c.value)}
                      className="flex items-center space-x-1 px-2 py-1 rounded border border-slate-800 bg-slate-950 text-[10px] text-slate-300 hover:border-slate-700"
                    >
                      <span className="w-2 h-2 rounded-full" style={{ backgroundColor: c.value }} />
                      <span>{c.label.split(' ')[0]}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Viewport Resolution */}
              <div className="grid grid-cols-2 gap-3 pt-2">
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Viewport Width (px)</label>
                  <input
                    type="number"
                    value={viewportWidth}
                    onChange={(e) => setViewportWidth(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white font-mono"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Viewport Height (px)</label>
                  <input
                    type="number"
                    value={viewportHeight}
                    onChange={(e) => setViewportHeight(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white font-mono"
                  />
                </div>
              </div>

              {/* Screencast Quality & FPS */}
              <div className="space-y-3 pt-2">
                <div>
                  <div className="flex justify-between text-slate-300 font-semibold mb-1">
                    <span>Screencast Frame Rate: {screencastFps} FPS</span>
                  </div>
                  <input
                    type="range"
                    min="5"
                    max="30"
                    value={screencastFps}
                    onChange={(e) => setScreencastFps(Number(e.target.value))}
                    className="w-full accent-blue-500"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-slate-300 font-semibold mb-1">
                    <span>JPEG Quality: {screencastQuality}%</span>
                  </div>
                  <input
                    type="range"
                    min="40"
                    max="100"
                    value={screencastQuality}
                    onChange={(e) => setScreencastQuality(Number(e.target.value))}
                    className="w-full accent-blue-500"
                  />
                </div>
              </div>
            </div>
          )}

          {activeTab === 'export' && (
            <div className="space-y-4">
              <div>
                <label className="block text-slate-300 font-semibold mb-1.5">Default Export Format</label>
                <select className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500">
                  <option value="pdf">One-Click PDF (WeasyPrint / A4)</option>
                  <option value="html">Standalone HTML Guide</option>
                  <option value="markdown">Raw GitHub-Flavored Markdown</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1.5">PDF Styling Theme</label>
                <select className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500">
                  <option value="modern">Modern Enterprise (Blue accents, callout cards)</option>
                  <option value="classic">Minimalist Technical Standard</option>
                  <option value="compact">Compact SOP Checklist</option>
                </select>
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3.5 border-t border-slate-800 bg-slate-950/80 flex items-center justify-between">
          <div className="flex items-center space-x-1.5">
            {saveSuccess && (
              <span className="flex items-center space-x-1 text-emerald-400 text-xs font-semibold animate-in fade-in">
                <CheckCircle2 className="w-4 h-4" />
                <span>Settings Saved & Applied</span>
              </span>
            )}
          </div>

          <div className="flex items-center space-x-2">
            <button
              type="button"
              onClick={closeSettingsModal}
              className="px-4 py-2 rounded-xl text-xs font-medium text-slate-400 hover:text-white hover:bg-slate-800 transition"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleSave}
              disabled={isSaving}
              className="flex items-center space-x-1.5 bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-xl text-xs font-semibold shadow-lg shadow-blue-600/20 transition disabled:opacity-50"
            >
              {isSaving ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
              <span>Save & Apply Settings</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
