import { useCallback } from 'react';
import { useAppContext } from '../store/AppContext';
import { Subject } from '../types';
import { api } from '../services/api';

export function useIngestion() {
  const { addToast, addOptimisticJob, refreshJobs } = useAppContext();

  const startIngestion = useCallback(async (
    url: string, 
    type: string, 
    targetSubject: Subject,
    tokensPerChunk?: number,
    tokensOverlap?: number,
    dataType?: 'video' | 'playlist'
  ) => {
    if (!targetSubject) return;

    // 1. Feedback imediato para o usuário
    addToast(`Started processing ${type} for "${targetSubject.name}"...`, 'info');
    
    // 2. Add optimistic job card immediately in Activity Monitor
    addOptimisticJob(`Ingesting ${type} for "${targetSubject.name}"...`);

    try {
      const response = await api.ingestYoutube({
        video_url: url,
        subject_id: targetSubject.id,
        tokens_per_chunk: tokensPerChunk,
        tokens_overlap: tokensOverlap,
        data_type: dataType,
      });

      if (response && response.job_id) {
        addToast(`Ingestion complete for "${targetSubject.name}"!`, 'success');
      } else {
        addToast(`Ingestion complete for "${targetSubject.name}"!`, 'success');
      }
    } catch (error: any) {
      console.error('Ingestion error:', error);
      if (error?.message === 'DUPLICATE_SOURCE') {
        addToast('This content has already been ingested. Skipping.', 'error');
      } else {
        addToast('Error connecting to the ingestion server.', 'error');
      }
    } finally {
      // 3. Refresh jobs to replace optimistic card with real server data
      await refreshJobs();
    }
  }, [addToast, addOptimisticJob, refreshJobs]);

  return { startIngestion };
}
