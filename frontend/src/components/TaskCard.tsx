import React from 'react';
import { useTranslation } from 'react-i18next';
import { IngestionTask } from '../types';
import { 
  CheckCircle2, Loader2, XCircle, ExternalLink, 
  Youtube, FileText, Newspaper, BookOpen, Globe, Database, Clock, 
  Layers, ChevronRight, AlertCircle, Calendar, Hash, Activity
} from 'lucide-react';
import { ErrorDetailModal } from './ErrorDetailModal';
import { useAppContext } from '../store/AppContext';
import { motion } from 'motion/react';

interface TaskCardProps {
  task: IngestionTask;
}

const getSourceIcon = (type?: string) => {
  switch (type?.toLowerCase()) {
    case 'youtube': return Youtube;
    case 'article': return Newspaper;
    case 'pdf': return FileText;
    case 'file': return FileText;
    case 'wikipedia': return BookOpen;
    case 'web': return Globe;
    default: return Database;
  }
};

const formatRelativeTime = (dateString: string, t: any) => {
  const normalizedDate = dateString.endsWith('Z') || dateString.includes('+') ? dateString : `${dateString}Z`;
  const date = new Date(normalizedDate);
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);
  
  if (diffInSeconds < 5) return t('common.time.now');
  if (diffInSeconds < 60) return `${diffInSeconds}s ${t('common.time.ago')}`;
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ${t('common.time.ago')}`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ${t('common.time.ago')}`;
  return date.toLocaleDateString();
};

export function TaskCard({ task }: TaskCardProps) {
  const { t } = useTranslation();
  const { setSelectedSourceIdForDb, setCurrentView } = useAppContext();
  const [isErrorModalOpen, setIsErrorModalOpen] = React.useState(false);
  
  const statusConfig = {
    pending: { color: 'text-zinc-500', bg: 'bg-zinc-500/10', border: 'border-zinc-500/20', icon: Clock, label: t('common.status.pending') },
    started: { color: 'text-blue-400', bg: 'bg-blue-400/10', border: 'border-blue-400/20', icon: Loader2, label: t('common.status.started'), animate: true },
    processing: { color: 'text-amber-400', bg: 'bg-amber-400/10', border: 'border-amber-400/20', icon: Loader2, label: t('common.status.processing'), animate: true },
    finished: { color: 'text-emerald-400', bg: 'bg-emerald-400/10', border: 'border-emerald-400/20', icon: CheckCircle2, label: t('common.status.completed') },
    done: { color: 'text-emerald-400', bg: 'bg-emerald-400/10', border: 'border-emerald-400/20', icon: CheckCircle2, label: t('common.status.completed') },
    failed: { color: 'text-rose-400', bg: 'bg-rose-400/10', border: 'border-rose-400/20', icon: AlertCircle, label: t('common.status.failed') },
    error: { color: 'text-rose-400', bg: 'bg-rose-400/10', border: 'border-rose-400/20', icon: AlertCircle, label: t('common.status.failed') },
    cancelled: { color: 'text-zinc-500', bg: 'bg-zinc-500/10', border: 'border-zinc-500/20', icon: XCircle, label: t('common.status.cancelled') }
  };

  const config = statusConfig[task.status] || statusConfig.pending;
  const isFailed = ['failed', 'error'].includes(task.status);
  const isProcessing = ['processing', 'started'].includes(task.status);
  const isCompleted = ['done', 'finished'].includes(task.status);
  const SourceIcon = getSourceIcon(task.ingestionType);

  const handleClick = () => {
    if (isFailed) setIsErrorModalOpen(true);
    else if (isCompleted && task.contentSourceId) {
      setSelectedSourceIdForDb(task.contentSourceId);
      setCurrentView('database');
    }
  };

  return (
    <>
      <motion.div 
        layout
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        whileHover={{ y: -2 }}
        onClick={handleClick}
        className={`group relative flex flex-col bg-zinc-900/40 backdrop-blur-md border ${config.border} rounded-2xl p-4 transition-all duration-300 ${
          isFailed || (isCompleted && task.contentSourceId) ? 'cursor-pointer hover:bg-zinc-800/60' : ''
        }`}
      >
        {/* Top Section: Icon & Identity */}
        <div className="flex items-start justify-between gap-3 mb-4">
          <div className="flex items-center gap-3 min-w-0">
            <div className={`p-2.5 rounded-xl bg-zinc-950 border border-white/5 shadow-inner text-zinc-400 group-hover:text-zinc-200 transition-colors`}>
              <SourceIcon className="w-5 h-5" />
            </div>
            <div className="min-w-0">
              <h4 className="text-[13px] font-bold text-zinc-100 truncate leading-tight tracking-tight mb-1" title={task.title}>
                {task.title}
              </h4>
              <div className="flex items-center gap-2">
                <span className="text-[9px] font-black px-1.5 py-0.5 rounded-md bg-white/5 text-zinc-500 border border-white/5 uppercase tracking-tighter">
                  {task.ingestionType || 'Unknown'}
                </span>
                <span className="text-[9px] font-mono text-zinc-600">
                  {task.id.substring(0, 8)}
                </span>
              </div>
            </div>
          </div>
          <div className="flex flex-col items-end shrink-0">
            <div className={`flex items-center gap-1.5 px-2 py-0.5 rounded-full border ${config.border} ${config.bg} ${config.color} text-[9px] font-black uppercase tracking-widest shadow-sm`}>
              {config.animate && <config.icon className="w-2.5 h-2.5 animate-spin" />}
              {!config.animate && <config.icon className="w-2.5 h-2.5" />}
              {config.label}
            </div>
            {isCompleted && (
              <span className="text-[10px] text-zinc-500 font-medium mt-1 pr-1">
                {formatRelativeTime(task.createdAt, t)}
              </span>
            )}
          </div>
        </div>

        {/* Content Section: Progress or Result */}
        <div className="flex-1">
          {isProcessing ? (
            <div className="space-y-3">
              <div className="flex justify-between items-center text-[10px] font-bold text-zinc-400">
                <div className="flex items-center gap-1.5">
                  <Activity className="w-3 h-3 text-amber-500 animate-pulse" />
                  <span className="uppercase tracking-wide">{task.statusMessage || t('common.status.processing')}</span>
                </div>
                <span className="text-amber-400 font-mono">{task.progress}%</span>
              </div>
              <div className="relative h-1.5 w-full bg-zinc-950 rounded-full overflow-hidden border border-white/5 shadow-inner">
                <motion.div 
                  initial={{ width: 0 }}
                  animate={{ width: `${task.progress}%` }}
                  className="absolute h-full bg-gradient-to-r from-amber-500 to-orange-400 rounded-full shadow-[0_0_10px_rgba(245,158,11,0.4)]"
                />
              </div>
              {task.currentStep && (
                <div className="flex items-center gap-1 text-[9px] font-bold text-zinc-600 uppercase tracking-widest">
                  <Layers className="w-2.5 h-2.5" />
                  <span>Phase {task.currentStep} <ChevronRight className="inline w-2 h-2" /> {task.totalSteps}</span>
                </div>
              )}
            </div>
          ) : isFailed ? (
            <div className="p-3 rounded-xl bg-rose-500/5 border border-rose-500/10 group-hover:border-rose-500/30 transition-colors">
              <p className="text-[11px] text-rose-400/80 leading-relaxed line-clamp-2 italic font-serif">
                "{task.errorMessage || 'Unknown system failure during ingestion.'}"
              </p>
              <div className="mt-2 flex items-center gap-1 text-[9px] font-black text-rose-500/60 uppercase tracking-widest">
                <AlertCircle className="w-3 h-3" />
                {t('common.actions.view_details')}
              </div>
            </div>
          ) : (
            <div className="flex flex-col gap-2.5">
              <div className="flex items-center justify-between p-2.5 rounded-xl bg-emerald-500/[0.03] border border-emerald-500/10">
                <div className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.6)]" />
                  <span className="text-[11px] text-zinc-400 font-medium">Pipeline optimized</span>
                </div>
                {task.chunksCount && (
                  <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-lg bg-zinc-900 border border-white/5 text-[10px] font-bold text-emerald-400">
                    <Database className="w-3 h-3" />
                    <span>{task.chunksCount}</span>
                  </div>
                )}
              </div>
              {!isCompleted && (
                 <div className="flex items-center gap-1.5 text-[10px] text-zinc-500 font-medium ml-1">
                    <Clock className="w-3.5 h-3.5" />
                    {formatRelativeTime(task.createdAt, t)}
                 </div>
              )}
            </div>
          )}
        </div>

        {/* Hover Action Indicator */}
        {(isFailed || (isCompleted && task.contentSourceId)) && (
          <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <div className="p-1 rounded-full bg-white/10 text-white backdrop-blur-md">
              <ChevronRight className="w-3 h-3" />
            </div>
          </div>
        )}
      </motion.div>

      <ErrorDetailModal 
        isOpen={isErrorModalOpen}
        onClose={() => setIsErrorModalOpen(false)}
        task={task}
      />
    </>
  );
}
