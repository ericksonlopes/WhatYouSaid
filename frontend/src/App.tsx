import React, {useState} from 'react';
import {useTranslation} from 'react-i18next';
import {ChevronLeft, ChevronRight, Plus, RefreshCw, Search, Database, Activity as ActivityIcon, Loader2, CheckCircle2, AlertCircle} from 'lucide-react';
import { motion } from 'motion/react';
import {AppProvider, useAppContext} from './store/AppContext';
import {Sidebar} from './components/Sidebar';
import {TaskCard} from './components/TaskCard';
import {SourcesTable} from './components/SourcesTable';
import {AddContentModal} from './components/AddContentModal';
import {ToastContainer} from './components/ToastContainer';
import {SearchView} from './components/SearchView';
import {ChunksViewer} from './components/ChunksViewer';
import {ErrorBoundary} from './components/ErrorBoundary';
import {ContentSource} from './types';

function ActivityMonitorView() {
  const { jobs = [], refreshJobs, isJobsLoaded, sources = [], addToast } = useAppContext();
  const { t } = useTranslation();
  const [page, setPage] = useState(1);
  const [isSyncing, setIsSyncing] = useState(false);
  const pageSize = 12;

  const handleRefresh = async () => {
    if (isSyncing) return;
    setIsSyncing(true);
    try {
      await refreshJobs?.();
      addToast(t('notifications.sync.success'), 'success');
    } catch (err) {
      addToast(t('notifications.sync.error'), 'error');
    } finally {
      setIsSyncing(false);
    }
  };

  const enrichedJobs = React.useMemo(() => {
    return jobs.map(job => {
      if (job.contentSourceId) {
        const source = sources.find(s => s.id === job.contentSourceId);
        if (source) {
          return { 
            ...job, 
            title: (job.title === job.statusMessage || job.title.includes('Job')) ? source.title : job.title,
            chunksCount: source.chunkCount || job.chunksCount
          };
        }
      }
      return job;
    });
  }, [jobs, sources]);

  const totalPages = Math.ceil(enrichedJobs.length / pageSize);
  const paginatedJobs = enrichedJobs.slice((page - 1) * pageSize, page * pageSize);

  const stats = React.useMemo(() => {
    return {
      total: enrichedJobs.length,
      processing: enrichedJobs.filter(j => ['processing', 'started'].includes(j.status)).length,
      completed: enrichedJobs.filter(j => ['done', 'finished'].includes(j.status)).length,
      failed: enrichedJobs.filter(j => ['failed', 'error'].includes(j.status)).length
    };
  }, [enrichedJobs]);

  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setPage(newPage);
    }
  };

  return (
    <div className="p-8 pt-10 max-w-7xl mx-auto h-full flex flex-col">
      {/* Header & Bento Stats */}
      <div className="mb-10 space-y-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3.5 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 shadow-[0_0_20px_rgba(16,185,129,0.1)]">
              <ActivityIcon className="w-7 h-7 text-emerald-400" />
            </div>
            <div>
              <h2 className="text-3xl font-black text-white tracking-tight leading-none">{t('activity.title')}</h2>
              <p className="text-zinc-500 text-sm mt-2 font-medium">{t('activity.subtitle')}</p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
             <div className="flex -space-x-2 mr-2">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="w-8 h-8 rounded-full border-2 border-bg-dark bg-zinc-800 flex items-center justify-center text-[10px] font-bold text-zinc-500">
                    {String.fromCharCode(65 + i)}
                  </div>
                ))}
             </div>
             <button 
                onClick={handleRefresh}
                disabled={isSyncing}
                className="group flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-zinc-300 bg-zinc-900 border border-white/5 rounded-lg hover:bg-zinc-800 hover:text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <RefreshCw className={`w-4 h-4 transition-transform duration-500 ${isSyncing ? 'animate-spin text-emerald-400' : 'group-hover:rotate-180'}`} />
                {isSyncing ? t('common.actions.syncing') : t('common.actions.sync')}
              </button>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: 'Pipeline Total', value: stats.total, color: 'text-zinc-400', icon: Database, bg: 'bg-zinc-400/5' },
            { label: 'Active Tasks', value: stats.processing, color: 'text-amber-400', icon: Loader2, bg: 'bg-amber-400/5', pulse: stats.processing > 0 },
            { label: 'Successfully Ingested', value: stats.completed, color: 'text-emerald-400', icon: CheckCircle2, bg: 'bg-emerald-400/5' },
            { label: 'Critical Errors', value: stats.failed, color: 'text-rose-400', icon: AlertCircle, bg: 'bg-rose-400/5' }
          ].map((stat, i) => (
            <motion.div 
              key={i} 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className={`relative overflow-hidden flex flex-col p-5 rounded-2xl border border-white/5 bg-zinc-900/40 backdrop-blur-sm ${stat.bg}`}
            >
              <div className="flex items-center justify-between mb-3">
                <stat.icon className={`w-4 h-4 ${stat.color} ${stat.pulse ? 'animate-spin' : ''}`} />
                <span className="text-[10px] font-black uppercase tracking-[0.2em] text-zinc-600">Metric</span>
              </div>
              <span className="text-3xl font-mono font-black text-white mb-1 leading-none">{stat.value}</span>
              <span className={`text-[10px] font-bold uppercase tracking-wider ${stat.color} opacity-80`}>{stat.label}</span>
              {stat.pulse && <div className="absolute top-0 right-0 w-1 h-full bg-amber-500 shadow-[0_0_15px_rgba(245,158,11,0.5)]" />}
            </motion.div>
          ))}
        </div>
      </div>

      <div className="flex-1 min-h-0 overflow-y-auto custom-scrollbar pr-1">
        {!isJobsLoaded && jobs.length === 0 ? (
          <div className="flex items-center justify-center py-20">
            <RefreshCw className="w-10 h-10 text-emerald-500 animate-spin opacity-20" />
          </div>
        ) : enrichedJobs.length === 0 ? (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex flex-col items-center justify-center py-32 text-center bg-zinc-900/20 border border-dashed border-white/5 rounded-3xl"
          >
            <div className="w-20 h-20 rounded-full bg-zinc-900 border border-white/5 flex items-center justify-center mb-6 shadow-2xl">
              <ActivityIcon className="w-10 h-10 text-zinc-800" />
            </div>
            <h3 className="text-zinc-200 font-bold text-xl mb-2">{t('activity.none')}</h3>
            <p className="text-zinc-500 text-sm max-w-sm mx-auto leading-relaxed">{t('activity.none_desc') || 'The ingestion pipeline is currently dormant. Initialize a data source to begin monitoring.'}</p>
          </motion.div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 pb-10 mt-6">
            {paginatedJobs.map(task => <TaskCard key={task.id} task={task} />)}
          </div>
        )}
      </div>

      {/* Pagination Footer */}
      {isJobsLoaded && enrichedJobs.length > pageSize && (
        <div className="mt-auto pt-8 border-t border-white/5 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-[10px] text-zinc-500 font-black uppercase tracking-widest">
              Live Monitor Active
            </span>
          </div>
          
          <div className="flex items-center gap-4">
            <span className="text-[11px] text-zinc-500 font-medium">
              Showing <span className="text-zinc-200 font-bold">{(page - 1) * pageSize + 1}</span> - <span className="text-zinc-200 font-bold">{Math.min(page * pageSize, enrichedJobs.length)}</span> of <span className="text-zinc-200 font-bold">{enrichedJobs.length}</span>
            </span>
            <div className="flex items-center gap-1.5 p-1 bg-zinc-950 rounded-xl border border-white/5">
              <button 
                onClick={() => handlePageChange(page - 1)}
                disabled={page === 1}
                className="p-2 rounded-lg hover:bg-zinc-800 text-zinc-500 hover:text-white disabled:opacity-20 transition-all"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <div className="text-[11px] font-black px-3 text-zinc-400">
                {page} <span className="mx-1 text-zinc-700">/</span> {totalPages}
              </div>
              <button 
                onClick={() => handlePageChange(page + 1)}
                disabled={page === totalPages}
                className="p-2 rounded-lg hover:bg-zinc-800 text-zinc-500 hover:text-white disabled:opacity-20 transition-all"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function ContentSourcesView() {
  const { setCurrentView, setSelectedSourceIdForDb, sources = [], isSourcesLoaded, refreshSources, refreshSubjects, selectedSubjects, addToast } = useAppContext();
  const { t } = useTranslation();
  const [searchQuery, setSearchQuery] = useState('');
  const [appliedSearchQuery, setAppliedSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState('all');
  const [page, setPage] = useState(1);
  const [isSyncing, setIsSyncing] = useState(false);
  const pageSize = 10;

  const filteredSources = React.useMemo(() => {
    let result = sources;
    
    // 1. Filter by subject context
    if (selectedSubjects.length > 0) {
      const selectedIds = new Set(selectedSubjects.map(s => s.id));
      result = result.filter(src => selectedIds.has(src.subjectId));
    }
    
    // 2. Filter by source type
    if (typeFilter !== 'all') {
      result = result.filter(src => src.type === typeFilter);
    }
    
    // 3. Filter by search query (only when applied)
    if (appliedSearchQuery.trim()) {
      const query = appliedSearchQuery.toLowerCase().trim();
      result = result.filter(src => 
        src.title.toLowerCase().includes(query) || 
        src.origin?.toLowerCase().includes(query)
      );
    }
    
    return result;
  }, [sources, selectedSubjects, typeFilter, appliedSearchQuery]);

  const handleSearchSubmit = () => {
    setAppliedSearchQuery(searchQuery);
    setPage(1); // Reset to first page on new search
  };

  const handleTypeChange = (newType: string) => {
    setTypeFilter(newType);
    setPage(1);
  };

  const handleRowClick = (source: ContentSource) => {
    setSelectedSourceIdForDb?.(source.id);
    setCurrentView?.('database');
  };

  const handleRefresh = async () => {
    if (isSyncing) return;
    setIsSyncing(true);
    try {
      await refreshSources?.();
      addToast(t('notifications.sync.success'), 'success');
    } catch (err) {
      addToast(t('notifications.sync.error'), 'error');
    } finally {
      setIsSyncing(false);
    }
  };

  return (
    <div className="p-8 max-w-6xl mx-auto h-full flex flex-col">
      <div className="mb-8 flex justify-between items-center">
        <div>
        <div className="flex items-center gap-3">
          <Database className="w-10 h-10 text-emerald-500" />
          <h2 className="text-2xl font-bold text-white tracking-tight">{t('sources.title')}</h2>
        </div>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-zinc-400">
              {selectedSubjects.length > 0 
                ? t('sources.subtitle.multiple', { count: selectedSubjects.length })
                : t('sources.subtitle.all')}
            </span>
            {selectedSubjects.length > 0 && (
              <div className="flex gap-1 overflow-hidden max-w-md">
                {selectedSubjects.map(s => (
                  <span key={s.id} className="text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-1.5 py-0.5 rounded truncate">
                    {s.name}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>

        <button 
          onClick={handleRefresh}
          disabled={isSyncing}
          className="group flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-zinc-300 bg-panel-bg border border-border-subtle rounded-lg hover:bg-panel-hover hover:text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <RefreshCw className={`w-4 h-4 transition-transform duration-500 ${isSyncing ? 'animate-spin text-emerald-400' : 'group-hover:rotate-180'}`} />
          {isSyncing ? t('common.actions.syncing') : t('common.actions.sync')}
        </button>
      </div>

      <div className="flex-1 min-h-0 flex flex-col">
        {!isSourcesLoaded && sources.length === 0 ? (
          <div className="flex items-center gap-3 text-zinc-500 text-sm">
            <RefreshCw className="w-4 h-4 animate-spin text-emerald-500" />
            {t('activity.loading')}
          </div>
        ) : (
          <>
            {filteredSources.length === 0 ? (
              <div className="flex flex-col h-full border border-border-subtle rounded-xl bg-panel-bg overflow-hidden">
                <SourcesTable 
                  sources={[]} 
                  totalCount={0}
                  page={1}
                  pageSize={pageSize}
                  onPageChange={setPage}
                  onRowClick={handleRowClick}
                  searchQuery={searchQuery}
                  onSearchChange={setSearchQuery}
                  onSearchSubmit={handleSearchSubmit}
                  typeFilter={typeFilter}
                  onTypeFilterChange={handleTypeChange}
                />
                <div className="flex-1 p-12 text-center text-zinc-500 bg-black/20 flex flex-col items-center justify-center gap-3">
                  <div className="w-12 h-12 rounded-full bg-zinc-900 border border-zinc-800 flex items-center justify-center">
                    <Search className="w-5 h-5 text-zinc-600" />
                  </div>
                  <div>
                    <p className="font-medium text-zinc-300">{t('sources.table.none')}</p>
                    <p className="text-sm text-zinc-500 mt-1 max-w-xs mx-auto">
                      {appliedSearchQuery || typeFilter !== 'all' 
                        ? `${t('search.results.none')}`
                        : t('sources.table.none')}
                    </p>
                    {appliedSearchQuery || typeFilter !== 'all' ? (
                      <button 
                        onClick={() => {
                          setSearchQuery('');
                          setAppliedSearchQuery('');
                          setTypeFilter('all');
                        }}
                        className="mt-4 text-xs text-emerald-500 hover:text-emerald-400 font-medium underline underline-offset-4"
                      >
                        {t('common.actions.clear')}
                      </button>
                    ) : (
                      <p className="mt-4 text-xs text-zinc-600">
                        {t('chat.locked.description')}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ) : (
              <SourcesTable 
                sources={filteredSources.slice((page - 1) * pageSize, page * pageSize)} 
                totalCount={filteredSources.length}
                page={page}
                pageSize={pageSize}
                onPageChange={setPage}
                onRowClick={handleRowClick}
                searchQuery={searchQuery}
                onSearchChange={setSearchQuery}
                onSearchSubmit={handleSearchSubmit}
                typeFilter={typeFilter}
                onTypeFilterChange={handleTypeChange}
              />
            )}
          </>
        )}
      </div>
    </div>
  );
}

// --- Main Layout ---
function MainContent() {
  const { currentView, selectedSubjects } = useAppContext();
  const { t } = useTranslation();
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);

  // @ts-ignore
  return (
    <div className="flex-1 flex flex-col h-screen overflow-hidden bg-bg-dark relative">
      {/* Topbar Context Indicator & Global Actions */}
      <header className="h-14 border-b border-border-subtle flex items-center justify-between px-6 bg-black/20 backdrop-blur-sm">
        <div className="flex items-center gap-2 text-sm">
          <span className="text-zinc-500">{t('sidebar.contexts.title')}:</span>
          <span className="text-emerald-400 font-medium px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20">
            {selectedSubjects.length === 1 
              ? selectedSubjects[0].name 
              : selectedSubjects.length > 1 
                ? `${selectedSubjects.length} ${t('sidebar.contexts.title')}`
                : t('sidebar.contexts.none')}
          </span>
        </div>
        
        <div className="flex items-center gap-3">
          <button 
            onClick={() => setIsAddModalOpen(true)}
            className="group flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-black bg-emerald-500 rounded-lg hover:bg-emerald-400 transition-colors shadow-[0_0_15px_rgba(16,185,129,0.2)]"
          >
            <Plus className="w-4 h-4 transition-transform duration-300 group-hover:rotate-90" />
            {t('common.actions.addData')}
          </button>
        </div>
      </header>

      {/* View Router */}
      <main className="flex-1 overflow-auto relative">
        <ErrorBoundary>
          {currentView === 'activity' && <ActivityMonitorView />}
          {currentView === 'sources' && <ContentSourcesView />}
          {currentView === 'chat' && (
            <div className="flex-1 flex flex-col items-center justify-center p-8 text-center">
              <div className="w-16 h-16 bg-zinc-800 rounded-full flex items-center justify-center mb-4">
                <span className="text-2xl">🔒</span>
              </div>
              <h2 className="text-xl font-semibold mb-2">{t('chat.locked.title')}</h2>
              <p className="text-zinc-400 max-w-md">
                {t('chat.locked.description')}
              </p>
            </div>
          )}
          {currentView === 'search' && <SearchView />}
          {currentView === 'database' && <ChunksViewer />}
        </ErrorBoundary>
      </main>

      {/* Modals & Overlays */}
      <AddContentModal 
        isOpen={isAddModalOpen} 
        onClose={() => setIsAddModalOpen(false)} 
      />
      <ToastContainer />
    </div>
  );
}

export default function App() {
  return (
    <AppProvider>
      <div className="flex h-screen w-full bg-bg-dark text-zinc-200 font-sans selection:bg-emerald-500/30">
        <Sidebar />
        <MainContent />
      </div>
    </AppProvider>
  );
}
