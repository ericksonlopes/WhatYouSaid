import React, { useState, useEffect } from 'react';
import { Search, Edit2, Trash2, Database, ChevronLeft, ChevronRight, Save, X, Loader2 } from 'lucide-react';
import { useAppContext } from '../store/AppContext';
import { api } from '../services/api';

export function ChunksViewer() {
  const { selectedSubjects, selectedSourceIdForDb, setSelectedSourceIdForDb, sources } = useAppContext();
  const [chunks, setChunks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [page, setPage] = useState(1);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editContent, setEditContent] = useState('');
  const pageSize = 10;

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const chunksData = await api.fetchChunks(
          selectedSourceIdForDb || undefined,
          100,
          0,
          searchQuery
        );
        setChunks(chunksData);
      } catch (err) {
        console.error('Error loading chunks:', err);
      } finally {
        setLoading(false);
      }
    };

    const debounceTimer = setTimeout(() => {
      loadData();
    }, 400);

    return () => clearTimeout(debounceTimer);
  }, [selectedSourceIdForDb, searchQuery]);

  const sourceMap = React.useMemo(() => {
    return new Map(sources.map(s => [s.id, s]));
  }, [sources]);

  // We now use chunks directly from the server-side filtered results
  const totalPages = Math.ceil(chunks.length / pageSize);
  const paginatedChunks = chunks.slice((page - 1) * pageSize, page * pageSize);

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this chunk?')) {
      try {
        await api.deleteChunk(id);
        setChunks(chunks.filter(c => c.id !== id));
      } catch (err) {
        console.error('Error deleting chunk:', err);
        alert('Failed to delete chunk.');
      }
    }
  };

  const handleEdit = (chunk: any) => {
    setEditingId(chunk.id);
    setEditContent(chunk.content);
  };

  const handleSave = async (id: string) => {
    try {
      await api.updateChunk(id, editContent);
      setChunks(chunks.map(c => c.id === id ? { ...c, content: editContent } : c));
      setEditingId(null);
    } catch (err) {
      console.error('Error updating chunk:', err);
      alert('Failed to update chunk.');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="w-8 h-8 text-emerald-500 animate-spin" />
      </div>
    );
  }

  return (
    <div className="p-8 max-w-7xl mx-auto h-full flex flex-col">
      <div className="mb-8 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
        <div>
          <h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <Database className="w-6 h-6 text-emerald-400" />
            Chunks Viewer
          </h2>
          <div className="flex flex-col sm:flex-row sm:items-center gap-3 mt-1">
            <p className="text-zinc-400">Manage and edit raw text chunks stored in SQLite & Weaviate.</p>
            {selectedSourceIdForDb && (
              <button 
                onClick={() => setSelectedSourceIdForDb(null)}
                className="flex items-center gap-1.5 px-2 py-0.5 w-fit text-xs font-medium text-emerald-400 bg-emerald-400/10 hover:bg-emerald-400/20 rounded-md transition-colors border border-emerald-400/20"
              >
                Filtered by Source
                <X className="w-3 h-3" />
              </button>
            )}
          </div>
        </div>
        <div className="relative w-full lg:w-64">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" />
          <input 
            type="text" 
            placeholder="Search chunks..." 
            value={searchQuery}
            onChange={(e) => { setSearchQuery(e.target.value); setPage(1); }}
            className="w-full bg-black/40 border border-border-subtle rounded-xl pl-9 pr-4 py-2 text-sm text-zinc-200 focus:outline-none focus:border-emerald-500/50 transition-colors"
          />
        </div>
      </div>

      {selectedSourceIdForDb && (
        <div className="mb-6">
          <p className="text-sm text-zinc-400 mb-2">Source ID: <span className="font-mono text-zinc-300">{selectedSourceIdForDb}</span></p>
          <p className="text-lg font-semibold text-white">Total chunks: {chunks.length}</p>
        </div>
      )}

      <div className="flex-1 min-h-0 flex flex-col overflow-hidden">
        <div className="overflow-y-auto flex-1 custom-scrollbar space-y-4 pr-2">
          {paginatedChunks.length === 0 ? (
            <div className="p-12 text-center text-zinc-500 bg-[#121212] border border-border-subtle rounded-2xl">
              No chunks found matching your criteria.
            </div>
          ) : (
            paginatedChunks.map((chunk, index) => (
              <div key={chunk.id} className="bg-[#121212] border border-border-subtle rounded-xl p-5 hover:border-zinc-700 transition-colors group">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
                  <div className="flex flex-col sm:flex-row sm:items-center gap-3">
                    <h3 className="text-sm font-bold text-white truncate max-w-[300px]">
                      {sourceMap.get(chunk.content_source_id)?.title || 'Unknown Source'} 
                      <span className="ml-2 text-zinc-500 font-normal">#{(page - 1) * pageSize + index + 1}</span>
                    </h3>
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="px-2 py-0.5 rounded bg-zinc-800/50 border border-zinc-700/50 text-[10px] text-zinc-400 whitespace-nowrap">
                        {chunk.content.length} chars
                      </span>
                      <span className="px-2 py-0.5 rounded bg-zinc-800/50 border border-zinc-700/50 text-[10px] text-zinc-400 whitespace-nowrap">
                        {chunk.tokens_count || 0} tokens
                      </span>
                      <span className="px-2 py-0.5 rounded bg-zinc-800/50 border border-zinc-700/50 text-[10px] text-zinc-400 uppercase">
                        pt
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between md:justify-end gap-4">
                    <span className="text-[10px] text-zinc-600 font-mono">ID: {chunk.id}</span>
                    <div className="flex items-center gap-1 opacity-100 md:opacity-0 md:group-hover:opacity-100 transition-opacity">
                      {editingId === chunk.id ? (
                        <>
                          <button onClick={() => handleSave(chunk.id)} className="p-1.5 bg-emerald-500/10 text-emerald-400 hover:bg-emerald-400/20 rounded transition-colors" title="Save">
                            <Save className="w-4 h-4" />
                          </button>
                          <button onClick={() => setEditingId(null)} className="p-1.5 bg-zinc-800 text-zinc-400 hover:bg-zinc-700 rounded transition-colors" title="Cancel">
                            <X className="w-4 h-4" />
                          </button>
                        </>
                      ) : (
                        <>
                          <button onClick={() => handleEdit(chunk)} className="p-1.5 bg-blue-500/10 text-blue-400 hover:bg-blue-400/20 rounded transition-colors" title="Edit Chunk">
                            <Edit2 className="w-4 h-4" />
                          </button>
                          <button onClick={() => handleDelete(chunk.id)} className="p-1.5 bg-red-500/10 text-red-400 hover:bg-red-400/20 rounded transition-colors" title="Delete Chunk">
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                </div>
                
                {editingId === chunk.id ? (
                  <textarea
                    value={editContent}
                    onChange={(e) => setEditContent(e.target.value)}
                    className="w-full h-32 bg-black/50 border border-emerald-500/50 rounded-lg p-3 text-sm text-zinc-200 focus:outline-none focus:ring-1 focus:ring-emerald-500/50 resize-none custom-scrollbar"
                  />
                ) : (
                  <p className="text-sm text-zinc-400 leading-relaxed">
                    {chunk.content}
                  </p>
                )}
              </div>
            ))
          )}
        </div>
        
        {/* Pagination */}
        {chunks.length > 0 && (
          <div className="pt-4 mt-4 border-t border-border-subtle flex items-center justify-between shrink-0">
            <span className="text-xs text-zinc-500">
              Showing {(page - 1) * pageSize + 1} to {Math.min(page * pageSize, chunks.length)} of {chunks.length} chunks
            </span>
            <div className="flex items-center gap-2">
              <button 
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="p-1.5 rounded-lg text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span className="text-xs font-medium text-zinc-300 px-2">
                Page {page} of {Math.max(1, totalPages)}
              </span>
              <button 
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page >= totalPages}
                className="p-1.5 rounded-lg text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
