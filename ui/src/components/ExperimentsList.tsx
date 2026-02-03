import React, { useEffect, useState } from 'react';
import { Card } from './Card';

const API_BASE = 'http://localhost:8000/v1';

interface Experiment {
    experiment_id: string;
    created_at: string;
    media_id: string;
    status: string;
    recommendation: string | null;
    decision: string | null;
}

interface ExperimentsListProps {
    onSelect: (experimentId: string) => void;
}

export const ExperimentsList: React.FC<ExperimentsListProps> = ({ onSelect }) => {
    const [experiments, setExperiments] = useState<Experiment[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchExperiments = async () => {
            try {
                const res = await fetch(`${API_BASE}/experiments`);
                if (!res.ok) throw new Error('Failed to fetch experiments');
                const data = await res.json();
                setExperiments(data);
            } catch (err: any) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchExperiments();
    }, []);

    if (loading) return <div className="text-gray-400 p-8">Loading experiments...</div>;
    if (error) return <div className="text-red-400 p-8">Error: {error}</div>;

    return (
        <div className="max-w-7xl mx-auto space-y-6">
            <h1 className="text-3xl font-bold text-white tracking-tight mb-8">Experiment History</h1>

            <div className="bg-black/20 border border-gray-800 rounded-lg overflow-hidden">
                <table className="w-full text-left text-sm text-gray-400">
                    <thead className="bg-gray-900/50 text-gray-200 uppercase font-semibold text-xs">
                        <tr>
                            <th className="px-6 py-4">Date</th>
                            <th className="px-6 py-4">Media ID / Name</th>
                            <th className="px-6 py-4">Status</th>
                            <th className="px-6 py-4">Recommendation</th>
                            <th className="px-6 py-4">Decision</th>
                            <th className="px-6 py-4">Action</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-800">
                        {experiments.length === 0 ? (
                            <tr>
                                <td colSpan={6} className="px-6 py-8 text-center text-gray-500">
                                    No experiments found. Start a new evaluation!
                                </td>
                            </tr>
                        ) : (
                            experiments.map((ex) => (
                                <tr
                                    key={ex.experiment_id}
                                    className="hover:bg-gray-900/40 transition-colors cursor-pointer"
                                    onClick={() => onSelect(ex.experiment_id)}
                                >
                                    <td className="px-6 py-4 font-mono text-gray-500">
                                        {new Date(ex.created_at).toLocaleString()}
                                    </td>
                                    <td className="px-6 py-4 font-medium text-white truncate max-w-xs" title={ex.media_id}>
                                        {ex.media_id}
                                    </td>
                                    <td className="px-6 py-4">
                                        <StatusBadge status={ex.status} />
                                    </td>
                                    <td className="px-6 py-4">
                                        {ex.recommendation ? (
                                            <span className="text-evals-green font-semibold">{ex.recommendation}</span>
                                        ) : (
                                            <span className="text-gray-600">-</span>
                                        )}
                                    </td>
                                    <td className="px-6 py-4">
                                        {ex.decision ? (
                                            <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${ex.decision === 'ship' ? 'bg-green-900/30 text-green-400' :
                                                    ex.decision === 'iterate' ? 'bg-yellow-900/30 text-yellow-400' :
                                                        'bg-red-900/30 text-red-400'
                                                }`}>
                                                {ex.decision}
                                            </span>
                                        ) : (
                                            <span className="text-gray-600">-</span>
                                        )}
                                    </td>
                                    <td className="px-6 py-4 text-right">
                                        <button className="text-evals-green hover:underline">View</button>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

const StatusBadge: React.FC<{ status: string }> = ({ status }) => {
    let color = 'text-gray-500';
    if (status === 'complete') color = 'text-green-400';
    if (status === 'failed') color = 'text-red-400';
    if (status === 'running') color = 'text-blue-400';
    if (status === 'awaiting_decision') color = 'text-yellow-400';

    return (
        <span className={`uppercase font-bold text-xs ${color}`}>
            {status.replace('_', ' ')}
        </span>
    );
};
