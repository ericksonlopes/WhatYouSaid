import React, { useState, useEffect } from 'react';
import { Plus, RefreshCw, Search, ChevronLeft, ChevronRight } from 'lucide-react';
import { AppProvider, useAppContext } from './store/AppContext';
import { Sidebar } from './components/Sidebar';
import { TaskCard } from './components/TaskCard';
import { SourcesTable } from './components/SourcesTable';
import { AddContentModal } from './components/AddContentModal';
import { ToastContainer } from './components/ToastContainer';
import { ChatView } from './components/ChatView';
import { SearchView } from './components/SearchView';
import { ChunksViewer } from './components/ChunksViewer';
import { IngestionTask, ContentSource } from './types';
import { api } from './services/api';

function ActivityMonitorView() {
  const { jobs = [], refreshJobs, isJobsLoaded } = useAppContext();
  const [page, setPage] = useState(1);
  const pageSize = 12;

  const totalPages = Math.ceil(jobs.length / pageSize);
  const paginatedJobs = jobs.slice((page - 1) * pageSize, page * pageSize);

  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setPage(newPage);
    }
  };

  return (
    <div className="p-8 max-w-5xl mx-auto h-full flex flex-col">
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-white tracking-tight">Activity Monitor</h2>
          <p className="text-zinc-400 mt-1">Real-time ingestion pipeline status.</p>
        </div>
        <button 
          onClick={() => refreshJobs?.()}
          className="p-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-400 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      <div className="flex-1 min-h-0 overflow-y-auto custom-scrollbar pr-1">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {!isJobsLoaded ? (
            <div className="text-zinc-500 text-sm">Loading activity pipeline...</div>
          ) : jobs.length === 0 ? (
            <div className="text-zinc-500 text-sm col-span-2 py-12 text-center bg-panel-bg border border-border-subtle rounded-xl">
              No recent activity.
            </div>
          ) : (
            paginatedJobs.map(task => <TaskCard key={task.id} task={task} />)
          )}
        </div>
      </div>

      {/* Pagination Footer */}
      {isJobsLoaded && jobs.length > pageSize && (
        <div className="mt-8 pt-6 border-t border-border-subtle flex items-center justify-between bg-bg-dark">
          <span className="text-xs text-zinc-500">
            Showing <span className="text-zinc-300 font-medium">{(page - 1) * pageSize + 1}</span> to <span className="text-zinc-300 font-medium">{Math.min(page * pageSize, jobs.length)}</span> of <span className="text-zinc-300 font-medium">{jobs.length}</span> tasks
          </span>
          <div className="flex items-center gap-2">
            <button 
              onClick={() => handlePageChange(page - 1)}
              disabled={page === 1}
              className="p-1.5 rounded-md border border-border-subtle bg-zinc-900/50 hover:bg-zinc-800 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="text-xs font-medium text-zinc-400 px-3">
              Page {page} of {totalPages}
            </span>
            <button 
              onClick={() => handlePageChange(page + 1)}
              disabled={page === totalPages}
              className="p-1.5 rounded-md border border-border-subtle bg-zinc-900/50 hover:bg-zinc-800 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function ContentSourcesView() {
  const { setCurrentView, setSelectedSourceIdForDb, sources = [], isSourcesLoaded, refreshSources, selectedSubjects } = useAppContext();
  const [searchQuery, setSearchQuery] = useState('');
  const [appliedSearchQuery, setAppliedSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState('all');
  const [page, setPage] = useState(1);
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
    await refreshSources?.();
  };

  return (
    <div className="p-8 max-w-6xl mx-auto h-full flex flex-col">
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-white tracking-tight">Content Sources</h2>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-zinc-400">
              {selectedSubjects.length > 0 
                ? `Showing sources for ${selectedSubjects.length} context(s).` 
                : "Showing all sources in the database."}
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
          className="p-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-400 transition-colors border border-zinc-700/50 shadow-sm"
          title="Refresh list"
        >
          <RefreshCw className={`w-4 h-4 ${!isSourcesLoaded ? 'animate-spin' : ''}`} />
        </button>
      </div>

      <div className="flex-1 min-h-0 flex flex-col">
        {/* Always show filters through SourcesTable (if not loading initial data) */}
        {!isSourcesLoaded && sources.length === 0 ? (
          <div className="flex items-center gap-3 text-zinc-500 text-sm">
            <RefreshCw className="w-4 h-4 animate-spin text-emerald-500" />
            Loading knowledge sources...
          </div>
        ) : (
          <>
            {filteredSources.length === 0 ? (
              <div className="flex flex-col h-full border border-border-subtle rounded-xl bg-panel-bg overflow-hidden">
                {/* Re-render just the header part of SourcesTable to keep filters accessible */}
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
                    <p className="font-medium text-zinc-300">No sources found.</p>
                    <p className="text-sm text-zinc-500 mt-1 max-w-xs mx-auto">
                      {appliedSearchQuery || typeFilter !== 'all' 
                        ? `Try adjusting your search for "${appliedSearchQuery || searchQuery}" or changing the filters.`
                        : "No sources found in the selected context(s). Try adding some content."}
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
                        Clear all filters
                      </button>
                    ) : (
                      /* Use the existing logic or trigger modal from MainContent if possible, 
                         but here we can just show a link to encourage action */
                      <p className="mt-4 text-xs text-zinc-600">
                        Click on "Add Data" in the top bar to begin.
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
function PlaceholderView({ title, description }: { title: string, description: string }) {
  return (
    <div className="p-8 h-full flex flex-col items-center justify-center text-center">
      <div className="w-16 h-16 rounded-2xl bg-panel-bg border border-border-subtle flex items-center justify-center mb-6">
        <span className="text-2xl">â¨</span>
      </div>
      <h2 className="text-2xl font-bold text-white tracking-tight">{title}</h2>
      <p className="text-zinc-400 mt-2 max-w-md">{description}</p>
    </div>
  );
}

// --- Main Layout ---
function MainContent() {
  const { currentView, selectedSubjects, addToast, refreshSubjects } = useAppContext();
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);

  const handleSync = async () => {
    if (isSyncing) return;
    setIsSyncing(true);
    
    try {
      await refreshSubjects();
      addToast('Data pipeline synchronized successfully!', 'success');
    } catch (err) {
      addToast('Sync failed.', 'error');
    } finally {
      setIsSyncing(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col h-screen overflow-hidden bg-bg-dark relative">
      {/* Topbar Context Indicator & Global Actions */}
      <header className="h-14 border-b border-border-subtle flex items-center justify-between px-6 bg-black/20 backdrop-blur-sm">
        <div className="flex items-center gap-2 text-sm">
          <span className="text-zinc-500">Context:</span>
          <span className="text-emerald-400 font-medium px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20">
            {selectedSubjects.length === 1 
              ? selectedSubjects[0].name 
              : selectedSubjects.length > 1 
                ? `${selectedSubjects.length} Contexts Selected`
                : 'None Selected'}
          </span>
        </div>
        
        <div className="flex items-center gap-3">
          <button 
            onClick={handleSync}
            disabled={isSyncing}
            className="group flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-zinc-300 bg-panel-bg border border-border-subtle rounded-lg hover:bg-panel-hover hover:text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <RefreshCw className={`w-4 h-4 transition-transform duration-500 ${isSyncing ? 'animate-spin text-emerald-400' : 'group-hover:rotate-180'}`} />
            {isSyncing ? 'Syncing...' : 'Sync'}
          </button>
          <button 
            onClick={() => setIsAddModalOpen(true)}
            className="group flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-black bg-emerald-500 rounded-lg hover:bg-emerald-400 transition-colors shadow-[0_0_15px_rgba(16,185,129,0.2)]"
          >
            <Plus className="w-4 h-4 transition-transform duration-300 group-hover:rotate-90" />
            Add Data
          </button>
        </div>
      </header>

      {/* View Router */}
      <main className="flex-1 overflow-auto relative">
        {currentView === 'activity' && <ActivityMonitorView />}
        {currentView === 'sources' && <ContentSourcesView />}
        {currentView === 'chat' && <ChatView />}
        {currentView === 'search' && <SearchView />}
        {currentView === 'database' && <ChunksViewer />}
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
