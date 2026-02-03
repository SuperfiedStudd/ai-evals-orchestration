import React from 'react';
import { Card } from './Card';

// Mock data interface
interface ResultRow {
    model: string;
    effort: string;
    quality: string;
    ready: string;
    cost: string;
    latency: string;
    isWinner?: boolean;
}

interface ResultsCardProps {
    results: ResultRow[] | null;
}

export const ResultsCard: React.FC<ResultsCardProps> = ({ results }) => {
    if (!results) return null;

    return (
        <Card title="Evaluation Results" className="col-span-full">
            <div className="overflow-x-auto">
                <table className="w-full text-sm text-left">
                    <thead className="text-gray-500 border-b border-gray-800">
                        <tr>
                            <th className="py-2">Model</th>
                            <th className="py-2">Edit Effort</th>
                            <th className="py-2">Structural Quality</th>
                            <th className="py-2">Publish-Ready</th>
                            <th className="py-2">Cost</th>
                            <th className="py-2">Latency</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-800">
                        {results.map((row) => (
                            <tr key={row.model} className={row.isWinner ? 'bg-gray-900/50' : ''}>
                                <td className="py-3 font-medium text-white flex items-center">
                                    {row.isWinner && <span className="text-evals-green mr-2">★</span>}
                                    {row.model}
                                </td>
                                <td className="py-3 text-gray-300">{row.effort}</td>
                                <td className="py-3 text-gray-300">{row.quality}</td>
                                <td className="py-3 text-gray-300">{row.ready}</td>
                                <td className="py-3 text-gray-300">{row.cost}</td>
                                <td className="py-3 text-gray-300">{row.latency}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </Card>
    );
};
