import React, { useState, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { X, User, Upload, FileAudio, RefreshCw, AlertCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { api } from '../../services/api';
import { useAppContext } from '../../store/AppContext';

interface AddVoiceProfileModalProps {
  onClose: () => void;
  onSuccess: () => void;
}

export const AddVoiceProfileModal: React.FC<AddVoiceProfileModalProps> = ({ onClose, onSuccess }) => {
  const { t } = useTranslation();
  const { addToast } = useAppContext();
  const [name, setName] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      addToast(t('diarization.train_modal.placeholder'), 'error');
      return;
    }
    if (!file) {
      addToast(t('diarization.notifications.file_selection_error'), 'error');
      return;
    }

    try {
      setLoading(true);
      const formData = new FormData();
      formData.append('name', name);
      formData.append('file', file);
      
      await api.registerVoiceProfile(formData);
      addToast(t('diarization.notifications.train_success', { name }), 'success');
      onSuccess();
      onClose();
    } catch (err: any) {
      addToast(err.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="absolute inset-0 bg-black/80 backdrop-blur-md"
        onClick={onClose}
      />
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 20 }}
        className="relative bg-zinc-950 border border-white/10 w-full max-w-lg rounded-3xl overflow-hidden shadow-2xl"
      >
        <div className="p-6 border-b border-white/5 flex items-center justify-between bg-zinc-900/30">
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-2xl bg-emerald-500/10 border border-emerald-500/20">
              <User className="w-6 h-6 text-emerald-400" />
            </div>
            <div>
              <h2 className="text-xl font-black text-white">{t('voices.new_btn')}</h2>
              <p className="text-zinc-500 text-[10px] font-bold uppercase tracking-[0.2em]">{t('diarization.train_modal.title')}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-xl text-zinc-500 hover:text-white hover:bg-white/5 transition-all"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          <div className="space-y-2">
            <label className="text-[10px] font-black text-zinc-500 uppercase tracking-[0.2em] ml-1">
              {t('diarization.train_modal.profile_name_label')}
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder={t('diarization.train_modal.placeholder')}
              className="w-full bg-zinc-900/50 border border-white/5 rounded-2xl px-5 py-4 text-white placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500/50 transition-all font-medium"
              disabled={loading}
              autoFocus
            />
          </div>

          <div className="space-y-2">
            <label className="text-[10px] font-black text-zinc-500 uppercase tracking-[0.2em] ml-1">
              {t('diarization.modal.file_tab')}
            </label>
            <div 
              onClick={() => !loading && fileInputRef.current?.click()}
              className={`
                relative h-40 border-2 border-dashed rounded-3xl flex flex-col items-center justify-center gap-4 transition-all cursor-pointer overflow-hidden group
                ${file ? 'border-emerald-500/50 bg-emerald-500/5' : 'border-white/5 bg-zinc-900/30 hover:bg-zinc-900/50 hover:border-white/10'}
                ${loading ? 'opacity-50 cursor-not-allowed' : ''}
              `}
            >
              {file ? (
                <>
                  <FileAudio className="w-10 h-10 text-emerald-400" />
                  <div className="text-center px-4">
                    <p className="text-white font-bold text-sm truncate max-w-[250px]">{file.name}</p>
                    <p className="text-zinc-500 text-[10px] font-bold uppercase tracking-wider mt-1">
                      {(file.size / (1024 * 1024)).toFixed(2)} MB
                    </p>
                  </div>
                </>
              ) : (
                <>
                  <div className="p-4 rounded-2xl bg-zinc-800 text-zinc-500 group-hover:text-emerald-400 group-hover:bg-emerald-500/10 transition-all">
                    <Upload className="w-8 h-8" />
                  </div>
                  <div className="text-center">
                    <p className="text-zinc-400 font-bold text-sm">{t('diarization.modal.drag_drop')}</p>
                    <p className="text-zinc-600 text-[10px] font-bold uppercase tracking-wider mt-1">{t('diarization.modal.supported_formats')}</p>
                  </div>
                </>
              )}
              <input
                ref={fileInputRef}
                type="file"
                accept="audio/*"
                onChange={handleFileChange}
                className="hidden"
              />
            </div>
          </div>

          <div className="pt-2">
            <button
              type="submit"
              disabled={loading || !name.trim() || !file}
              className={`
                w-full py-4 rounded-2xl font-black text-xs uppercase tracking-[0.2em] transition-all flex items-center justify-center gap-3
                ${loading || !name.trim() || !file
                  ? 'bg-zinc-900 text-zinc-700 cursor-not-allowed border border-white/5'
                  : 'bg-emerald-500 text-black hover:bg-emerald-400 shadow-lg shadow-emerald-500/20 active:scale-[0.98]'}
              `}
            >
              {loading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>{t('diarization.status.steps.recognizing')}</span>
                </>
              ) : (
                <>
                  <User className="w-4 h-4" />
                  <span>{t('diarization.train_modal.save_btn')}</span>
                </>
              )}
            </button>
          </div>
        </form>

        <div className="px-6 py-4 bg-zinc-900/20 border-t border-white/5 flex items-start gap-3">
          <AlertCircle className="w-4 h-4 text-zinc-500 shrink-0 mt-0.5" />
          <p className="text-[10px] text-zinc-600 leading-relaxed font-medium">
            {t('diarization.train_modal.desc')}
          </p>
        </div>
      </motion.div>
    </div>
  );
};
