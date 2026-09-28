import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useDocumentStore } from '../../store/documentStore';
import { FileText, Sparkles, AlertCircle, Info, Lightbulb } from 'lucide-react';

export const MarkdownPreview: React.FC = () => {
  const { currentDocument, isGenerating, selectedStepNumber, setSelectedStepNumber } = useDocumentStore();

  if (isGenerating) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-8 text-center space-y-4 bg-slate-900/30 border border-slate-800/80 rounded-xl h-full">
        <div className="relative">
          <div className="w-12 h-12 rounded-full border-2 border-blue-500/20 border-t-blue-500 animate-spin" />
          <Sparkles className="w-5 h-5 text-blue-400 absolute inset-0 m-auto" />
        </div>
        <div>
          <h3 className="text-sm font-semibold text-white">LangGraph Multi-Agent Engine Active</h3>
          <p className="text-xs text-slate-400 mt-1 max-w-sm">
            Intent Parser ➔ Technical Writer ➔ Quality Reviewer synthesizing procedural guide...
          </p>
        </div>
      </div>
    );
  }

  if (!currentDocument) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-8 text-center space-y-3 bg-slate-900/30 border border-slate-800/80 rounded-xl h-full">
        <div className="w-12 h-12 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-500">
          <FileText className="w-6 h-6" />
        </div>
        <div>
          <p className="text-xs font-semibold text-slate-300">No Documentation Generated Yet</p>
          <p className="text-[11px] text-slate-500 max-w-xs mt-0.5">
            Complete a recording session and trigger LangGraph generation to preview the live manual.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col h-full bg-slate-900/40 border border-slate-800/80 rounded-xl overflow-hidden shadow-xl">
      {/* Document Top Bar */}
      <div className="h-9 bg-slate-900 border-b border-slate-800 px-4 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <FileText className="w-3.5 h-3.5 text-blue-400" />
          <span className="text-xs font-bold text-slate-200 truncate">{currentDocument.title}</span>
        </div>
        <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700/60 font-mono">
          v{currentDocument.version}
        </span>
      </div>

      {/* Document Body */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 text-slate-200 text-xs leading-relaxed">
        {/* Summary Card */}
        {currentDocument.executive_summary && (
          <div className="bg-blue-950/20 border-l-4 border-blue-500 p-3.5 rounded-r-lg">
            <h4 className="font-semibold text-blue-400 text-xs mb-1">Executive Summary</h4>
            <p className="text-slate-300">{currentDocument.executive_summary}</p>
          </div>
        )}

        {/* Prerequisites */}
        {currentDocument.prerequisites && currentDocument.prerequisites.length > 0 && (
          <div className="bg-slate-950/60 border border-slate-800 rounded-lg p-3.5">
            <h4 className="font-semibold text-slate-300 text-xs mb-2">Prerequisites</h4>
            <ul className="list-disc list-inside space-y-1 text-slate-400">
              {currentDocument.prerequisites.map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Steps List */}
        <div className="space-y-4">
          <h3 className="font-bold text-sm text-white">Procedural Steps</h3>
          {currentDocument.steps.map((step) => {
            const isSelected = selectedStepNumber === step.step_number;
            return (
              <div
                key={step.step_number}
                onClick={() => setSelectedStepNumber(isSelected ? null : step.step_number)}
                className={`p-4 rounded-xl border transition cursor-pointer ${
                  isSelected
                    ? 'bg-slate-800/70 border-blue-500 ring-1 ring-blue-500/50 shadow-md'
                    : 'bg-slate-950/70 border-slate-800/90 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center space-x-2.5 mb-2">
                  <span className="w-5 h-5 rounded-full bg-blue-600 text-white flex items-center justify-center text-[10px] font-bold">
                    {step.step_number}
                  </span>
                  <h4 className="font-bold text-xs text-white">{step.title}</h4>
                </div>

                <p className="text-slate-300 mb-3">{step.instruction}</p>

                {step.screenshot_url && (
                  <div className="my-3 rounded-lg overflow-hidden border border-slate-800 bg-black/40">
                    <img
                      src={step.screenshot_url}
                      alt={`Step ${step.step_number} Highlight`}
                      className="w-full h-auto object-cover max-h-64"
                    />
                  </div>
                )}

                {step.callouts && step.callouts.length > 0 && (
                  <div className="space-y-2 mt-3">
                    {step.callouts.map((callout, cIdx) => (
                      <div
                        key={cIdx}
                        className={`flex items-start space-x-2 text-[11px] p-2.5 rounded-lg border ${
                          callout.type === 'warning'
                            ? 'bg-amber-950/30 border-amber-800/60 text-amber-300'
                            : callout.type === 'tip'
                            ? 'bg-emerald-950/30 border-emerald-800/60 text-emerald-300'
                            : 'bg-blue-950/30 border-blue-800/60 text-blue-300'
                        }`}
                      >
                        {callout.type === 'warning' ? (
                          <AlertCircle className="w-3.5 h-3.5 mt-0.5 shrink-0" />
                        ) : callout.type === 'tip' ? (
                          <Lightbulb className="w-3.5 h-3.5 mt-0.5 shrink-0" />
                        ) : (
                          <Info className="w-3.5 h-3.5 mt-0.5 shrink-0" />
                        )}
                        <span>{callout.content}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
