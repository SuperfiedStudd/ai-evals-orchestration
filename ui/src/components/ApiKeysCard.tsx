import React from 'react';
import { Card } from './Card';

interface ApiKeysCardProps {
    selectedModels: string[];
}

export const ApiKeysCard: React.FC<ApiKeysCardProps> = ({ selectedModels }) => {
    return (
        <Card title="API Keys" description="Bring your own API keys (never stored)">
            <div className="space-y-4">
                {selectedModels.length === 0 && (
                    <div className="text-sm text-gray-500 italic pb-2">Select models to enter keys</div>
                )}
                {selectedModels.map(model => (
                    <div key={model}>
                        <label className="block text-xs text-gray-400 mb-1">{model} Key</label>
                        <input
                            type="password"
                            className="w-full bg-black border border-gray-700 rounded px-3 py-2 text-sm text-white focus:border-evals-green focus:outline-none transition-colors"
                            placeholder="sk-..."
                        />
                    </div>
                ))}
            </div>
            <div className="mt-4 text-xs text-gray-600">
                Keys are passed directly to the model provider and are not persisted.
            </div>
        </Card>
    );
};
