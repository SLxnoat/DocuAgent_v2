import React, { useState, useRef, useEffect } from 'react';
import { MessageSquare, Send, Sparkles, User, Bot, Loader2, Target } from 'lucide-react';
import { useDocumentStore } from '../../store/documentStore';
import { documentsApi } from '../../api/documents';
import { ChatMessage } from '../../types/chat';

export const ChatPane: React.FC = () => {
  const {
    currentDocument,
    chatMessages,
    addChatMessage,
    updateSteps,
    selectedStepNumber,
    setSelectedStepNumber,
  } = useDocumentStore();

  const [inputPrompt, setInputPrompt] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatMessages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputPrompt.trim() || !currentDocument || isSubmitting) return;

    const userMsg: ChatMessage = {
      id: `msg_${Date.now()}`,
      role: 'user',
      content: inputPrompt,
      timestamp: new Date().toISOString(),
      step_number: selectedStepNumber || undefined,
    };

    addChatMessage(userMsg);
    const userText = inputPrompt;
    setInputPrompt('');
    setIsSubmitting(true);

    try {
      const response = await documentsApi.refineDocument({
        document_id: currentDocument.id,
        prompt: userText,
        target_step_number: selectedStepNumber || undefined,
        history: [...chatMessages, userMsg],
      });

      const assistantMsg: ChatMessage = {
        id: `msg_${Date.now() + 1}`,
        role: 'assistant',
        content: response.reply_message,
        timestamp: new Date().toISOString(),
        step_number: selectedStepNumber || undefined,
        applied_changes: {
          modified_steps: response.modified_step_numbers,
        },
      };

      addChatMessage(assistantMsg);
      updateSteps(response.updated_steps, response.updated_markdown);
    } catch (err) {
      console.error('Refinement failed:', err);
      addChatMessage({
        id: `msg_${Date.now() + 1}`,
        role: 'assistant',
        content: 'Failed to apply refinement. Please verify backend connection.',
        timestamp: new Date().toISOString(),
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-900/60 overflow-hidden">
      {/* Pane Header */}
      <div className="h-12 border-b border-slate-800 px-4 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <MessageSquare className="w-4 h-4 text-blue-400" />
          <h3 className="text-xs font-bold text-white uppercase tracking-wider">HITL Refiner</h3>
        </div>
        {selectedStepNumber && (
          <div className="flex items-center space-x-1.5 px-2 py-0.5 rounded-full bg-blue-950 border border-blue-800 text-[10px] text-blue-400 font-medium">
            <Target className="w-3 h-3" />
            <span>Targeting Step {selectedStepNumber}</span>
            <button
              onClick={() => setSelectedStepNumber(null)}
              className="ml-1 text-slate-400 hover:text-white"
            >
              ×
            </button>
          </div>
        )}
      </div>

      {/* Messages List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3.5 text-xs">
        {chatMessages.length === 0 && (
          <div className="text-center py-10 space-y-2 text-slate-500">
            <Bot className="w-8 h-8 mx-auto text-slate-600" />
            <p className="font-semibold text-slate-400">Human-in-the-Loop Refinement</p>
            <p className="text-[11px] max-w-xs mx-auto text-slate-500">
              Request targeted edits e.g. "Add a security note to step 2", "Omit login flow", or "Rephrase summary".
            </p>
          </div>
        )}

        {chatMessages.map((msg) => (
          <div
            key={msg.id}
            className={`flex items-start space-x-2.5 ${
              msg.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''
            }`}
          >
            <div
              className={`w-6 h-6 rounded-full flex items-center justify-center shrink-0 ${
                msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-300'
              }`}
            >
              {msg.role === 'user' ? <User className="w-3.5 h-3.5" /> : <Sparkles className="w-3.5 h-3.5" />}
            </div>

            <div
              className={`max-w-[80%] rounded-xl p-3 ${
                msg.role === 'user'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'bg-slate-950 border border-slate-800 text-slate-200 shadow-sm'
              }`}
            >
              <p className="text-xs leading-relaxed">{msg.content}</p>
            </div>
          </div>
        ))}
        {isSubmitting && (
          <div className="flex items-center space-x-2 text-slate-400 text-xs pl-2">
            <Loader2 className="w-3.5 h-3.5 animate-spin text-blue-400" />
            <span>Refiner Agent modifying documentation...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <form onSubmit={handleSendMessage} className="p-3 border-t border-slate-800 bg-slate-900/80">
        <div className="relative">
          <input
            type="text"
            value={inputPrompt}
            onChange={(e) => setInputPrompt(e.target.value)}
            disabled={!currentDocument || isSubmitting}
            placeholder={
              selectedStepNumber
                ? `Refine Step ${selectedStepNumber}...`
                : 'Ask refiner agent to modify manual...'
            }
            className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-3 pr-10 py-2.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 transition disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!inputPrompt.trim() || !currentDocument || isSubmitting}
            className="absolute right-2 top-2 p-1 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-3.5 h-3.5" />
          </button>
        </div>
      </form>
    </div>
  );
};
