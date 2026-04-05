import React, {useEffect, useRef, useState, type SyntheticEvent} from 'react';
import {Bot, PlayCircle, Send, User, Sparkles, MessageSquare, Plus} from 'lucide-react';
import { AnimatePresence, motion } from 'framer-motion';
import {useAppContext} from '../store/AppContext';
import {ChatMessage, Citation} from '../types';
import {api} from "../services/api";
import {LocalContextSelector} from './LocalContextSelector';

export function ChatView() {
  const { subjects, selectedSubjects, setSelectedSubjects } = useAppContext();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSendMessage = async (e: SyntheticEvent<HTMLFormElement> | React.KeyboardEvent<HTMLTextAreaElement>) => {
    e.preventDefault();
    if (!inputValue.trim() || selectedSubjects.length === 0) return;

    const userQuery = inputValue.trim();
    const newUserMsg: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: userQuery,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, newUserMsg]);
    setInputValue('');
    setIsTyping(true);

    try {
      // 1. Fetch real context using the search API with multiple subjects
      const subjectIds = selectedSubjects.map(s => s.id);
      const searchData = await api.search(userQuery, 5, subjectIds);
      
      // 2. Map citations from real search results
      const realCitations: Citation[] = searchData.results.map((res: any) => ({
        id: res.id,
        sourceId: res.content_source_id,
        title: res.extra?.subject_name || res.external_source || 'Fonte de Conhecimento',
        timestamp: res.extra?.timestamp || '',
        textSnippet: res.content || '',
        relevanceScore: res.score || 0
      }));

      // 3. Construct a "RAG response" 
      const hasResults = realCitations.length > 0;
      const contextNames = selectedSubjects.map(s => s.name).join(', ');
      
      const aiContent = hasResults 
        ? `Encontrei ${realCitations.length} trechos relevantes em seu ecossistema selecionado (${contextNames}) que podem responder à sua pergunta. Veja os detalhes abaixo.`
        : `Pesquisei em "${contextNames}" mas não encontrei informações específicas que correspondam à sua consulta. Tente adicionar mais dados ou reformular a pergunta.`;

      const newAiMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: aiContent,
        citations: realCitations,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, newAiMsg]);
    } catch (err) {
      console.error('Chat error:', err);
      const errorMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: "Ocorreu um erro ao pesquisar em sua base de conhecimento. Verifique se o servidor está ativo.",
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleSubjectsChange = (ids: string[]) => {
    const selected = subjects.filter(s => ids.includes(s.id));
    setSelectedSubjects(selected);
  };

  const selectedIds = selectedSubjects.map(s => s.id);

  if (selectedSubjects.length === 0) {
    return (
      <div className="h-full flex flex-col items-center justify-center p-8 bg-gradient-to-b from-[#1a1c20]/20 to-transparent">
        <motion.div 
          initial={{ opacity: 0, scale: 0.9, filter: 'blur(10px)' }}
          animate={{ opacity: 1, scale: 1, filter: 'blur(0px)' }}
          className="relative max-w-lg w-full text-center"
        >
          {/* Animated Background Rings */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-primary-500/10 blur-[100px] rounded-full animate-pulse" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-32 h-32 border border-primary-500/20 rounded-full animate-ping opacity-20" />
          
          <div className="relative z-10 bg-white/5 border border-white/10 rounded-[2.5rem] p-10 backdrop-blur-2xl shadow-2xl">
            <div className="w-20 h-20 mx-auto bg-gradient-to-br from-primary-500 to-primary-600 rounded-3xl flex items-center justify-center shadow-lg shadow-primary-500/20 mb-8 transform -rotate-3 hover:rotate-0 transition-transform duration-500 focus-ring">
              <Sparkles className="w-10 h-10 text-white" />
            </div>

            <h2 className="text-3xl font-bold text-white mb-4 tracking-tight">O que vamos explorar hoje?</h2>
            <p className="text-gray-400 text-lg leading-relaxed mb-10 px-4">
              Para começar uma conversa inteligente, selecione as bases de conhecimento que deseja consultar.
            </p>

            <div className="max-w-[280px] mx-auto">
              <LocalContextSelector
                mode="multi"
                selectedIds={selectedIds}
                onChange={handleSubjectsChange}
                placeholder="Selecionar Bases..."
                className="shadow-xl"
              />
            </div>

            <div className="mt-8 pt-8 border-t border-white/5 flex items-center justify-center gap-6">
              <div className="flex flex-col items-center gap-1">
                <div className="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center text-gray-500">
                  <Plus size={14} />
                </div>
                <span className="text-[10px] text-gray-500 uppercase font-black tracking-widest">Adicionar</span>
              </div>
              <div className="flex flex-col items-center gap-1">
                <div className="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center text-gray-500">
                  <MessageSquare size={14} />
                </div>
                <span className="text-[10px] text-gray-500 uppercase font-black tracking-widest">Conversar</span>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col relative overflow-hidden bg-gradient-to-b from-[#1a1c20]/10 to-transparent">
      {/* Scrollable Messages */}
      <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-10 custom-scrollbar pb-48">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center opacity-40 py-20">
            <motion.div
              animate={{ y: [0, -10, 0] }}
              transition={{ repeat: Infinity, duration: 4, ease: "easeInOut" }}
            >
              <Bot className="w-16 h-16 text-primary-500 mb-6" />
            </motion.div>
            <h3 className="text-xl font-semibold text-white mb-3">Assistente Ativo</h3>
            <p className="text-gray-400 max-w-sm text-sm">
              Estou pronto para pesquisar em {selectedSubjects.length} bases selecionadas. 
              Como posso te ajudar agora?
            </p>
          </div>
        ) : (
          messages.map((msg) => (
            <div key={msg.id} className={`flex gap-6 max-w-5xl mx-auto ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
              <div className={`w-10 h-10 rounded-2xl flex items-center justify-center flex-shrink-0 mt-1 shadow-lg transition-transform hover:scale-110 ${
                msg.role === 'user' 
                  ? 'bg-zinc-800 border border-white/5 text-zinc-300' 
                  : 'bg-primary-500 text-white'
              }`}>
                {msg.role === 'user' ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
              </div>

              <div className={`flex flex-col gap-3 min-w-0 max-w-[85%] ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                <div className={`px-6 py-4 rounded-[2rem] text-[15px] leading-relaxed shadow-xl ${
                  msg.role === 'user' 
                    ? 'bg-primary-500/10 text-zinc-100 rounded-tr-none border border-primary-500/20' 
                    : 'bg-white/5 text-gray-200 border border-white/5'
                }`}>
                  {msg.content}
                </div>

                {msg.role === 'assistant' && msg.citations && msg.citations.length > 0 && (
                  <div className="flex flex-wrap gap-2.5 mt-1">
                    {msg.citations.map((cit, idx) => (
                      <button 
                        key={cit.id}
                        className="group flex items-center gap-3 p-3 rounded-2xl bg-white/5 border border-white/5 hover:border-primary-500/30 hover:bg-white/10 transition-all text-left max-w-full"
                        onClick={() => alert(`Fonte: ${cit.title}\n\n"${cit.textSnippet}"`)}
                      >
                        <div className="flex items-center justify-center w-6 h-6 rounded-lg bg-primary-500/20 text-[10px] text-primary-400 font-bold group-hover:bg-primary-500 group-hover:text-white transition-colors">
                          {idx + 1}
                        </div>
                        <div className="flex flex-col overflow-hidden pr-2">
                          <span className="text-[11px] font-bold text-gray-300 truncate lowercase tracking-tight">{cit.title}</span>
                          {cit.timestamp && (
                            <span className="text-[9px] text-primary-500/80 font-mono flex items-center gap-1 mt-0.5">
                              <PlayCircle size={10} /> {cit.timestamp}
                            </span>
                          )}
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        
        {isTyping && (
          <div className="flex gap-6 max-w-5xl mx-auto items-center">
            <div className="w-10 h-10 rounded-2xl bg-primary-500 text-white flex items-center justify-center flex-shrink-0 shadow-lg shadow-primary-500/20">
              <Bot className="w-5 h-5" />
            </div>
            <div className="flex items-center gap-1.5 p-4 bg-white/5 rounded-full border border-white/5">
              <motion.div animate={{ scale: [1, 1.5, 1] }} transition={{ repeat: Infinity, duration: 1 }} className="w-1.5 h-1.5 rounded-full bg-primary-500/60" />
              <motion.div animate={{ scale: [1, 1.5, 1] }} transition={{ repeat: Infinity, duration: 1, delay: 0.2 }} className="w-1.5 h-1.5 rounded-full bg-primary-500/60" />
              <motion.div animate={{ scale: [1, 1.5, 1] }} transition={{ repeat: Infinity, duration: 1, delay: 0.4 }} className="w-1.5 h-1.5 rounded-full bg-primary-500/60" />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Modern Fixed Input Bar */}
      <div className="absolute bottom-0 left-0 right-0 p-6 z-30">
        <div className="max-w-5xl mx-auto relative">
          <div className="absolute -top-12 left-1/2 -translate-x-1/2 flex items-center gap-2 mb-4">
             <LocalContextSelector
                mode="multi"
                selectedIds={selectedIds}
                onChange={handleSubjectsChange}
                placeholder="Selecionar Bases"
                className="w-auto min-w-[200px]"
                compact
              />
          </div>

          <form 
            onSubmit={handleSendMessage}
            className="group relative flex items-end gap-3 bg-white/10 backdrop-blur-2xl border border-white/10 rounded-[2.5rem] p-3 shadow-2xl shadow-black/40 focus-within:border-primary-500/50 transition-all duration-300"
          >
            <div className="flex-1 min-h-[48px] flex items-center px-4">
               <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage(e);
                  }
                }}
                placeholder={`Perguntar em ${selectedSubjects.length} base${selectedSubjects.length > 1 ? 's' : ''}...`}
                className="w-full max-h-40 min-h-[24px] bg-transparent text-[15px] text-gray-100 placeholder:text-gray-500 resize-none focus:outline-none py-1 custom-scrollbar"
                rows={1}
              />
            </div>
            
            <button
              type="submit"
              disabled={!inputValue.trim() || isTyping}
              className="w-12 h-12 rounded-full bg-primary-500 text-white flex items-center justify-center shadow-lg shadow-primary-500/30 hover:bg-primary-400 active:scale-95 disabled:opacity-30 disabled:hover:bg-primary-500 transition-all duration-300 group/btn"
            >
              <Send className="w-5 h-5 transition-transform duration-300 group-hover/btn:translate-x-0.5 group-hover/btn:-translate-y-0.5" />
            </button>
          </form>
          
          <div className="text-center mt-3">
            <p className="text-[10px] text-gray-500 font-medium uppercase tracking-[0.2em] opacity-50">
              RAG Engine v2.0 • 2026 Semantic Hub
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
