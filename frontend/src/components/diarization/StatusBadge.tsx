import React from 'react';
import { Clock, Loader2, CheckCircle2, AlertCircle, Play } from 'lucide-react';

interface StatusBadgeProps {
    readonly status: 'completed' | 'pending' | 'processing' | 'failed' | 'ready';
    readonly message?: string;
    readonly size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, message, size = 'md' }) => {
    const isSm = size === 'sm';
    
    switch (status) {
        case 'completed':
            return (
                <div className={`inline-flex items-center gap-1.5 ${isSm ? 'px-2 py-0.5' : 'px-3 py-1'} rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-black uppercase ${isSm ? 'text-[8px]' : 'text-[10px]'} tracking-widest`}>
                    <CheckCircle2 className={isSm ? 'w-2.5 h-2.5' : 'w-3.5 h-3.5'} />
                    Pronto
                </div>
            );
        case 'ready':
            return (
                <div className={`inline-flex items-center gap-1.5 ${isSm ? 'px-2 py-0.5' : 'px-3 py-1'} rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 font-black uppercase ${isSm ? 'text-[8px]' : 'text-[10px]'} tracking-widest animate-pulse`}>
                    <Play className={isSm ? 'w-2.5 h-2.5' : 'w-3.5 h-3.5'} />
                    Identificar
                </div>
            );
        case 'processing':
            return (
                <div className={`inline-flex items-center gap-1.5 ${isSm ? 'px-2 py-0.5' : 'px-3 py-1'} rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 font-black uppercase ${isSm ? 'text-[8px]' : 'text-[10px]'} tracking-widest`} title={message}>
                    <Loader2 className={`${isSm ? 'w-2.5 h-2.5' : 'w-3.5 h-3.5'} animate-spin`} />
                    Processando
                </div>
            );
        case 'failed':
            return (
                <div className={`inline-flex items-center gap-1.5 ${isSm ? 'px-2 py-0.5' : 'px-3 py-1'} rounded-full bg-rose-500/10 border border-rose-500/20 text-rose-400 font-black uppercase ${isSm ? 'text-[8px]' : 'text-[10px]'} tracking-widest`} title={message}>
                    <AlertCircle className={isSm ? 'w-2.5 h-2.5' : 'w-3.5 h-3.5'} />
                    Erro
                </div>
            );
        default:
            return (
                <div className={`inline-flex items-center gap-1.5 ${isSm ? 'px-2 py-0.5' : 'px-3 py-1'} rounded-full bg-zinc-500/10 border border-zinc-500/20 text-zinc-400 font-black uppercase ${isSm ? 'text-[8px]' : 'text-[10px]'} tracking-widest`}>
                    <Clock className={isSm ? 'w-2.5 h-2.5' : 'w-3.5 h-3.5'} />
                    Pendente
                </div>
            );
    }
};
