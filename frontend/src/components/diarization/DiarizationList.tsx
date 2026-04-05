import React from 'react';
import { useTranslation } from 'react-i18next';
import { motion } from 'motion/react';
import { Search, Plus, Mic, Loader2, Video, FileText, Trash2, Edit2, Check, ExternalLink } from 'lucide-react';
import { StatusBadge } from './StatusBadge';
import { DiarizationJob } from './types';

interface DiarizationListProps {
    readonly jobs: DiarizationJob[];
    readonly isLoading: boolean;
    readonly searchQuery: string;
    readonly onSearchChange: (q: string) => void;
    readonly onOpenJob: (job: DiarizationJob) => void;
    readonly onDeleteJob: (id: string) => void;
    readonly onNewJob: () => void;
    readonly onEditJob: (job: DiarizationJob) => void;
    readonly editingJobId: string | null;
    readonly editingTitle: string;
    readonly onEditingTitleChange: (t: string) => void;
    readonly onSaveEdit: (id: string) => void;
    readonly onCancelEdit: () => void;
}

export const DiarizationList: React.FC<DiarizationListProps> = ({
    jobs,
    isLoading,
    searchQuery,
    onSearchChange,
    onOpenJob,
    onDeleteJob,
    onNewJob,
    onEditJob,
    editingJobId,
    editingTitle,
    onEditingTitleChange,
    onSaveEdit,
    onCancelEdit
}) => {
    const { t } = useTranslation();

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-8 h-full flex flex-col"
        >
            <div className="mb-8 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="p-3 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 shadow-[0_0_20px_rgba(16,185,129,0.1)]">
                        <Mic className="w-7 h-7 text-emerald-400" />
                    </div>
                    <div>
                        <h2 className="text-3xl font-black text-white tracking-tight leading-none">{t('diarization.title')}</h2>
                        <p className="text-zinc-500 text-sm mt-2 font-medium">{t('diarization.subtitle')}</p>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    <div className="relative group/search">
                        <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500 group-focus-within/search:text-emerald-500 transition-colors" />
                        <input
                            type="text"
                            value={searchQuery}
                            onChange={(e) => onSearchChange(e.target.value)}
                            placeholder="Buscar..."
                            className="w-48 pl-9 pr-3 py-1.5 bg-zinc-900 border border-white/5 rounded-lg text-sm text-zinc-300 focus:outline-none focus:border-emerald-500/30 transition-all font-medium"
                        />
                    </div>
                    
                    <button
                        onClick={onNewJob}
                        className="flex items-center gap-2 px-4 py-2 bg-emerald-500 text-black font-black uppercase text-[10px] tracking-widest rounded-xl hover:bg-emerald-400 transition-all shadow-[0_0_15px_rgba(16,185,129,0.2)]"
                    >
                        <Plus className="w-4 h-4 stroke-[3px]" />
                        {t('diarization.new_btn')}
                    </button>
                </div>
            </div>

            <div className="flex-1 bg-zinc-900/40 border border-white/5 rounded-2xl backdrop-blur-sm flex flex-col shadow-2xl overflow-hidden">
                <div className="overflow-x-auto overflow-y-auto custom-scrollbar flex-1">
                    <table className="w-full text-left border-separate border-spacing-0 table-fixed min-w-[1000px]">
                        <thead className="sticky top-0 z-10">
                            <tr className="border-b border-white/5 text-[10px] font-black text-zinc-500 uppercase tracking-widest bg-black/20 backdrop-blur-md">
                                <th className="w-14 pl-5 py-4 text-center">Icon</th>
                                <th className="w-[30%] pl-2 pr-4 py-4 text-left">{t('diarization.table.name')}</th>
                                <th className="w-40 px-4 py-4 text-left">{t('diarization.table.date')}</th>
                                <th className="w-24 px-4 py-4 text-center">{t('diarization.table.type')}</th>
                                <th className="w-28 px-4 py-4 text-left">{t('diarization.table.model')}</th>
                                <th className="w-24 px-4 py-4 text-center">{t('diarization.table.duration')}</th>
                                <th className="w-40 px-4 py-4 text-left">{t('diarization.table.status')}</th>
                                <th className="w-36 px-6 py-4 text-right">{t('diarization.table.actions')}</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/[0.03]">
                            {isLoading ? (
                                <tr>
                                    <td colSpan={8} className="py-24 text-center">
                                        <div className="flex flex-col items-center justify-center text-zinc-500">
                                            <Loader2 className="w-8 h-8 animate-spin mb-4 text-emerald-500" />
                                            <p className="text-[10px] font-black uppercase tracking-widest opacity-50">{t('diarization.table.loading')}</p>
                                        </div>
                                    </td>
                                </tr>
                            ) : jobs.length === 0 ? (
                                <tr>
                                    <td colSpan={8} className="py-24 text-center">
                                        <div className="flex flex-col items-center justify-center text-zinc-500 gap-4">
                                            <Mic className="w-12 h-12 opacity-10" />
                                            <p className="text-[10px] font-black uppercase tracking-widest opacity-30">{t('diarization.table.none')}</p>
                                        </div>
                                    </td>
                                </tr>
                            ) : (
                                jobs.map((job, index) => (
                                    <motion.tr
                                        key={job.id}
                                        initial={{ opacity: 0, x: -10 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ delay: index * 0.02 }}
                                        onClick={() => onOpenJob(job)}
                                        className="hover:bg-white/5 cursor-pointer transition-all group relative border-b border-transparent hover:border-white/5"
                                    >
                                        <td className="pl-5 pr-2 py-3">
                                            <div className="w-9 h-9 rounded-xl bg-emerald-500/10 flex items-center justify-center text-emerald-400 group-hover:bg-emerald-500 group-hover:text-black transition-colors flex-shrink-0">
                                                {job.sourceType === 'youtube' ? <Video className="w-4 h-4" /> : <FileText className="w-4 h-4" />}
                                            </div>
                                        </td>
                                        <td className="pl-2 pr-4 py-3">
                                            {editingJobId === job.id ? (
                                                <div className="flex items-center gap-1 min-w-0" onClick={e => e.stopPropagation()}>
                                                    <input
                                                        type="text"
                                                        autoFocus
                                                        value={editingTitle}
                                                        onChange={e => onEditingTitleChange(e.target.value)}
                                                        onKeyDown={e => {
                                                            if (e.key === 'Enter') onSaveEdit(job.id);
                                                            if (e.key === 'Escape') onCancelEdit();
                                                        }}
                                                        className="flex-1 bg-zinc-900 border border-emerald-500/50 rounded-lg px-2 py-1 text-sm text-white focus:outline-none min-w-0 font-medium"
                                                    />
                                                    <button onClick={() => onSaveEdit(job.id)} className="p-1 text-emerald-400 hover:bg-emerald-500/20 rounded-md">
                                                        <Check className="w-4 h-4" />
                                                    </button>
                                                </div>
                                            ) : (
                                                <div className="min-w-0">
                                                    <span className="text-sm font-bold text-zinc-100 group-hover:text-white transition-colors truncate block">{job.title}</span>
                                                    <div className="flex items-center gap-2 mt-0.5">
                                                        <span className="text-[9px] font-black uppercase tracking-widest text-zinc-600 group-hover:text-zinc-500">ID: {job.id.slice(0, 8)}</span>
                                                    </div>
                                                </div>
                                            )}
                                        </td>
                                        <td className="px-4 py-3 text-xs font-medium text-zinc-500 font-mono tracking-tighter uppercase whitespace-nowrap">
                                            {job.date}
                                        </td>
                                        <td className="px-4 py-3 text-center">
                                            <div className="flex justify-center">
                                                {job.sourceType === 'youtube' ? (
                                                    <span className="inline-flex items-center px-1.5 py-0.5 rounded bg-rose-500/10 border border-rose-500/10 text-[9px] font-black text-rose-400 uppercase tracking-widest" title="YouTube">
                                                        YT
                                                    </span>
                                                ) : (
                                                    <span className="inline-flex items-center px-1.5 py-0.5 rounded bg-blue-500/10 border border-blue-500/10 text-[9px] font-black text-blue-400 uppercase tracking-widest" title="Upload">
                                                        UP
                                                    </span>
                                                )}
                                            </div>
                                        </td>
                                        <td className="px-4 py-3">
                                            <span className="text-[10px] font-black text-zinc-400 uppercase tracking-widest">{job.modelSize}</span>
                                        </td>
                                        <td className="px-4 py-3 text-center">
                                             <span className="text-[10px] font-black text-zinc-500 uppercase tracking-widest font-mono">{job.duration || '--:--'}</span>
                                        </td>
                                        <td className="px-4 py-3">
                                            <StatusBadge status={job.status} message={job.statusMessage || job.errorMessage} size="sm" />
                                        </td>
                                        <td className="px-6 py-3">
                                            <div className="flex items-center justify-end gap-1.5 p-1 bg-white/[0.03] border border-white/5 rounded-2xl opacity-0 group-hover:opacity-100 transition-all">
                                                <button
                                                    onClick={(e) => { e.stopPropagation(); onEditJob(job); }}
                                                    className="w-8 h-8 flex items-center justify-center text-zinc-500 hover:text-white hover:bg-white/5 rounded-xl transition-all"
                                                    title="Renomear"
                                                >
                                                    <Edit2 className="w-3.5 h-3.5" />
                                                </button>
                                                <button
                                                    onClick={(e) => { e.stopPropagation(); onDeleteJob(job.id); }}
                                                    className="w-8 h-8 flex items-center justify-center text-zinc-500 hover:text-rose-500 hover:bg-rose-500/10 rounded-xl transition-all"
                                                    title="Excluir"
                                                >
                                                    <Trash2 className="w-3.5 h-3.5" />
                                                </button>
                                                <div className="w-8 h-8 flex items-center justify-center text-emerald-400 bg-emerald-500/10 rounded-xl">
                                                    <ExternalLink className="w-3.5 h-3.5" />
                                                </div>
                                            </div>
                                        </td>
                                    </motion.tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </motion.div>
    );
};
