import React, { useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { X, Video, Upload, Plus, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { api } from '../../services/api';
import { useAppContext } from '../../store/AppContext';

interface NewDiarizationModalProps {
    isOpen: boolean;
    onClose: () => void;
    onStart: () => void;
}

export const NewDiarizationModal: React.FC<NewDiarizationModalProps> = ({ isOpen, onClose, onStart }) => {
    const { t } = useTranslation();
    const { addToast, selectedSubjects } = useAppContext();
    const [uploadType, setUploadType] = useState<'file' | 'youtube'>('file');
    const [youtubeLink, setYoutubeLink] = useState('');
    const [file, setFile] = useState<File | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [language, setLanguage] = useState('pt');
    const [modelSize, setModelSize] = useState('base');

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            setFile(e.target.files[0]);
        }
    };

    const handleStartProcessing = async () => {
        if (uploadType === 'youtube' && !youtubeLink) {
            addToast(t('diarization.notifications.youtube_link_error'), 'error');
            return;
        }
        if (uploadType === 'file' && !file) {
            addToast(t('diarization.notifications.file_selection_error'), 'error');
            return;
        }

        setIsSubmitting(true);
        try {
            const subjectId = selectedSubjects[0]?.id;
            
            if (uploadType === 'youtube') {
                await api.startAudioProcessing({
                    source_type: 'youtube',
                    source: youtubeLink,
                    language,
                    model_size: modelSize,
                    recognize_voices: true,
                    subject_id: subjectId
                });
            } else {
                const formData = new FormData();
                formData.append('file', file!);
                const uploadResult = await api.ingestFile(formData);
                const s3Path = uploadResult?.s3_path || uploadResult?.file_path || '';

                await api.startAudioProcessing({
                    source_type: 'upload',
                    source: s3Path,
                    language,
                    model_size: modelSize,
                    recognize_voices: true,
                    subject_id: subjectId
                });
            }

            onClose();
            setFile(null);
            setYoutubeLink('');
            addToast(t('diarization.notifications.start_success'), 'success');
            onStart();
        } catch (err) {
            console.error('Failed to start processing:', err);
            addToast(t('diarization.notifications.start_error'), 'error');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="absolute inset-0 bg-black/80 backdrop-blur-sm"
                    />
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 20 }}
                        className="relative w-full max-w-lg bg-zinc-900 border border-white/10 rounded-3xl overflow-hidden shadow-2xl"
                    >
                        <div className="p-6 border-b border-white/5 flex items-center justify-between">
                            <h3 className="text-xl font-black text-white uppercase tracking-tight">{t('diarization.modal.new_title')}</h3>
                            <button onClick={onClose} className="p-2 hover:bg-white/5 rounded-xl transition-colors">
                                <X className="w-5 h-5 text-zinc-500" />
                            </button>
                        </div>
                        
                        <div className="p-6 space-y-6">
                            <div className="flex p-1 bg-black/40 rounded-2xl border border-white/5">
                                <button
                                    onClick={() => setUploadType('file')}
                                    className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${uploadType === 'file' ? 'bg-zinc-800 text-white shadow-xl' : 'text-zinc-500 hover:text-zinc-300'}`}
                                >
                                    <Upload className="w-4 h-4" />
                                    {t('diarization.modal.file_tab')}
                                </button>
                                <button
                                    onClick={() => setUploadType('youtube')}
                                    className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${uploadType === 'youtube' ? 'bg-zinc-800 text-white shadow-xl' : 'text-zinc-500 hover:text-zinc-300'}`}
                                >
                                    <Video className="w-4 h-4" />
                                    YouTube
                                </button>
                            </div>

                            {uploadType === 'youtube' ? (
                                <div className="space-y-2">
                                    <label className="text-[10px] font-black text-zinc-500 uppercase tracking-widest ml-1">{t('diarization.modal.video_url_label')}</label>
                                    <input
                                        type="text"
                                        value={youtubeLink}
                                        onChange={(e) => setYoutubeLink(e.target.value)}
                                        placeholder="https://youtube.com/watch?v=..."
                                        className="w-full px-4 py-3 bg-black/40 border border-white/5 rounded-xl text-sm text-white focus:outline-none focus:border-emerald-500/30 transition-all"
                                    />
                                </div>
                            ) : (
                                <div className="space-y-2">
                                    <label className="text-[10px] font-black text-zinc-500 uppercase tracking-widest ml-1">{t('diarization.modal.supported_formats')}</label>
                                    <div 
                                        onClick={() => fileInputRef.current?.click()}
                                        className="w-full h-32 border-2 border-dashed border-white/5 rounded-2xl flex flex-col items-center justify-center gap-3 cursor-pointer hover:bg-white/5 hover:border-emerald-500/20 transition-all group"
                                    >
                                        <input type="file" ref={fileInputRef} onChange={handleFileChange} className="hidden" accept="audio/*,video/*" />
                                        <div className="p-3 rounded-xl bg-zinc-800 text-zinc-400 group-hover:bg-emerald-500 group-hover:text-black transition-all">
                                            <Upload className="w-5 h-5" />
                                        </div>
                                        <span className="text-xs font-bold text-zinc-500 group-hover:text-zinc-300">
                                            {file ? file.name : t('diarization.modal.drag_drop')}
                                        </span>
                                    </div>
                                </div>
                            )}

                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <label className="text-[10px] font-black text-zinc-500 uppercase tracking-widest ml-1">{t('diarization.modal.language_label')}</label>
                                    <select
                                        value={language}
                                        onChange={(e) => setLanguage(e.target.value)}
                                        className="w-full px-4 py-3 bg-black/40 border border-white/5 rounded-xl text-sm text-white focus:outline-none focus:border-emerald-500/30 transition-all appearance-none"
                                    >
                                        <option value="pt">Português</option>
                                        <option value="en">English</option>
                                        <option value="es">Español</option>
                                    </select>
                                </div>
                                <div className="space-y-2">
                                    <label className="text-[10px] font-black text-zinc-500 uppercase tracking-widest ml-1">{t('diarization.modal.model_label')}</label>
                                    <select
                                        value={modelSize}
                                        onChange={(e) => setModelSize(e.target.value)}
                                        className="w-full px-4 py-3 bg-black/40 border border-white/5 rounded-xl text-sm text-white focus:outline-none focus:border-emerald-500/30 transition-all appearance-none"
                                    >
                                        <option value="base">{t('diarization.modal.models.base')}</option>
                                        <option value="small">{t('diarization.modal.models.small')}</option>
                                        <option value="medium">{t('diarization.modal.models.medium')}</option>
                                        <option value="large-v2">{t('diarization.modal.models.large')}</option>
                                    </select>
                                </div>
                            </div>
                        </div>

                        <div className="p-6 bg-black/20 border-t border-white/5 flex gap-3">
                            <button
                                onClick={onClose}
                                className="flex-1 py-3 px-4 rounded-xl text-[10px] font-black uppercase tracking-widest border border-white/10 text-zinc-400 hover:bg-white/5 transition-all"
                            >
                                {t('common.actions.cancel')}
                            </button>
                            <button
                                onClick={handleStartProcessing}
                                disabled={isSubmitting}
                                className="flex-1 py-3 px-4 bg-emerald-500 text-black font-black uppercase text-[10px] tracking-widest rounded-xl hover:bg-emerald-400 transition-all shadow-[0_0_20px_rgba(16,185,129,0.2)] disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                            >
                                {isSubmitting ? (
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                ) : (
                                    <Plus className="w-4 h-4 stroke-[3px]" />
                                )}
                                {t('diarization.modal.start_btn')}
                            </button>
                        </div>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
};
