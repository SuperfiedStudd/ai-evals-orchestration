import React, { useEffect, useState } from 'react';

const API_BASE = 'http://localhost:8000/v1';

interface DetailedRun {
    run_id: string;
    model_name: string;
    raw_output: string;
    latency_ms: number;
    cost_usd: number;
    metrics: {
        scores: Array<{
            metric_name: string;
            score: number;
            reasoning: string;
        }>;
    } | null;
}

interface ExperimentDetails {
    experiment: {
        experiment_id: string;
        created_at: string;
        media_id: string;
        status: string;
        recommendation: string | null;
        recommendation_reason: string | null;
        decision: string | null;
        decision_reason: string | null;
        tradeoffs: any;
        error_log: string | null;
    };
    runs: DetailedRun[];
}

interface ExperimentDetailViewProps {
    experimentId: string;
    onBack: () => void;
}

export const ExperimentDetailView: React.FC<ExperimentDetailViewProps> = ({ experimentId, onBack }) => {
    const [data, setData] = useState<ExperimentDetails | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Collapsible states for raw output
    const [openOutputs, setOpenOutputs] = useState<Record<string, boolean>>({});

    useEffect(() => {
        const fetchDetails = async () => {
            try {
                const res = await fetch(`${API_BASE}/experiments/${experimentId}/details`);
                if (!res.ok) throw new Error('Failed to fetch details');
                const json = await res.json();
                console.log("Detail JSON:", json);
                setData(json);
            } catch (err: any) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };
        fetchDetails();
    }, [experimentId]);

    const toggleOutput = (runId: string) => {
        setOpenOutputs(prev => ({ ...prev, [runId]: !prev[runId] }));
    };

    if (loading) return <div className="p-12 text-gray-400">Loading details...</div>;
    if (error) return <div className="p-12 text-red-400">Error: {error} <button onClick={onBack} className="text-white underline ml-4">Go Back</button></div>;
    if (!data) return null;

    const { experiment, runs } = data;

    return (
        <div className="max-w-7xl mx-auto space-y-8 animate-fade-in pb-20">
            {/* Header */}
            <div className="flex items-center justify-between">
                <button onClick={onBack} className="text-gray-500 hover:text-white flex items-center gap-2 text-sm font-medium">
                    ← Back to List
                </button>
                <div className="text-xs text-gray-600 font-mono">{experiment.experiment_id}</div>
            </div>

            <div className="bg-black/20 border border-gray-800 rounded-lg p-6">
                <div className="flex justify-between items-start mb-4">
                    <div>
                        <h1 className="text-2xl font-bold text-white">{experiment.media_id}</h1>
                        <p className="text-gray-500 text-sm">{new Date(experiment.created_at).toLocaleString()}</p>
                    </div>
                    <div className="text-right">
                        <div className="text-sm text-gray-400 uppercase tracking-wider">Status</div>
                        <div className={`text-xl font-bold uppercase ${experiment.status === 'failed' ? 'text-red-500' :
                                experiment.status === 'complete' ? 'text-evals-green' : 'text-blue-400'
                            }`}>
                            {experiment.status.replace('_', ' ')}
                        </div>
                    </div>
                </div>

                {experiment.error_log && (
                    <div className="mt-4 p-4 bg-red-900/20 border border-red-800 rounded text-red-200 font-mono text-sm whitespace-pre-wrap">
                        <strong>Error Log:</strong><br />
                        {experiment.error_log}
                    </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6 pt-6 border-t border-gray-800">
                    <div>
                        <h3 className="text-gray-400 text-xs uppercase font-semibold mb-2">Recommendation</h3>
                        {experiment.recommendation ? (
                            <div className="bg-evals-green/10 border border-evals-green/30 p-4 rounded">
                                <div className="text-evals-green text-lg font-bold mb-1">{experiment.recommendation}</div>
                                <p className="text-gray-300 text-sm">{experiment.recommendation_reason}</p>
                            </div>
                        ) : (
                            <div className="text-gray-600 italic">No recommendation yet</div>
                        )}
                    </div>
                    <div>
                        <h3 className="text-gray-400 text-xs uppercase font-semibold mb-2">Human Decision</h3>
                        {experiment.decision ? (
                            <div className="bg-gray-900 border border-gray-700 p-4 rounded">
                                <div className="text-white text-lg font-bold mb-1 uppercase">{experiment.decision}</div>
                                <p className="text-gray-400 text-sm">{experiment.decision_reason || "No reason recorded"}</p>
                            </div>
                        ) : (
                            <div className="text-gray-600 italic">No decision yet</div>
                        )}
                    </div>
                </div>
            </div>

            {/* Runs Table */}
            <h2 className="text-xl font-bold text-white mt-12 mb-4">Model Runs & Metrics</h2>
            <div className="space-y-4">
                {runs.map(run => {
                    const isWinner = experiment.recommendation === run.model_name;
                    return (
                        <div key={run.run_id} className={`bg-black/20 border rounded-lg overflow-hidden ${isWinner ? 'border-evals-green shadow-[0_0_15px_rgba(0,255,0,0.1)]' : 'border-gray-800'}`}>
                            <div className="p-4 flex items-center justify-between bg-gray-900/30">
                                <div className="flex items-center gap-4">
                                    <div className="text-lg font-bold text-white">{run.model_name}</div>
                                    {isWinner && <span className="text-[10px] bg-evals-green text-black px-2 py-0.5 rounded font-bold uppercase">Winner</span>}
                                </div>
                                <div className="flex gap-6 text-sm">
                                    <div className="text-gray-400">Latency: <span className="text-white font-mono">{run.latency_ms}ms</span></div>
                                    <div className="text-gray-400">Cost: <span className="text-white font-mono">${run.cost_usd.toFixed(4)}</span></div>
                                </div>
                            </div>

                            {/* Metrics Grid */}
                            <div className="p-4 grid grid-cols-1 md:grid-cols-3 gap-4 border-b border-gray-800">
                                {run.metrics?.scores.map(s => (
                                    <div key={s.metric_name} className="bg-black p-3 rounded border border-gray-800">
                                        <div className="flex justify-between mb-1">
                                            <span className="text-xs text-gray-500 uppercase">{s.metric_name.replace('_', ' ')}</span>
                                            <span className={`text-sm font-bold ${s.score >= 4 ? 'text-evals-green' : 'text-white'}`}>{s.score}/5</span>
                                        </div>
                                        <p className="text-xs text-gray-500 line-clamp-2" title={s.reasoning}>{s.reasoning}</p>
                                    </div>
                                )) || <div className="text-gray-600 text-sm italic">Metrics not found</div>}
                            </div>

                            {/* Raw Output Toggle */}
                            <div className="border-t border-gray-800">
                                <button
                                    className="w-full text-left px-4 py-2 text-xs text-gray-500 hover:text-white hover:bg-gray-900 transition-colors flex items-center gap-2"
                                    onClick={() => toggleOutput(run.run_id)}
                                >
                                    <span>{openOutputs[run.run_id] ? '▼ Hide' : '▶ Show'} Raw Output</span>
                                </button>
                                {openOutputs[run.run_id] && (
                                    <pre className="p-4 text-xs text-gray-300 font-mono bg-black overflow-x-auto whitespace-pre-wrap border-t border-gray-800">
                                        {run.raw_output}
                                    </pre>
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};
