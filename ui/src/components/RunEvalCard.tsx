import React from 'react';
import { Card } from './Card';

interface RunEvalCardProps {
    ready: boolean;
    onRun: () => void;
    loading: boolean;
    loadingText?: string;
}

export const RunEvalCard: React.FC<RunEvalCardProps> = ({ ready, onRun, loading, loadingText }) => {
    return (
        <Card title="Run Evaluation" description="Execute identical editing task across models">
            <button
                onClick={onRun}
                disabled={!ready || loading}
                className={`w-full py-3 rounded font-medium text-sm transition-all ${ready && !loading
                    ? 'bg-evals-green text-black hover:bg-green-400 shadow-[0_0_10px_rgba(57,255,20,0.3)]'
                    : 'bg-gray-800 text-gray-500 cursor-not-allowed'
                    }`}
            >
                {loading ? (
                    <span className="flex items-center justify-center">
                        <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-current" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        {loadingText || 'Running Evaluation...'}
                    </span>
                ) : 'Run Evaluation'}
            </button>
        </Card>
    );
};
