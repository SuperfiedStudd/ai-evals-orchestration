import React from 'react';
import { Card } from './Card';

export interface ModelConfig {
    id: string;
    name: string;
    provider: string;
    apiKey: string;
}

interface ModelConfigCardProps {
    models: ModelConfig[];
    onChange: (models: ModelConfig[]) => void;
}

const MAX_MODELS = 3;

export const ModelConfigCard: React.FC<ModelConfigCardProps> = ({ models, onChange }) => {

    const updateModel = (index: number, field: keyof ModelConfig, value: string) => {
        const newModels = [...models];
        newModels[index] = { ...newModels[index], [field]: value };
        onChange(newModels);
    };

    // Ensure there are always 3 slots for visual consistency, or we can just render strict list + add button.
    // Requirement: "Render 3 model slots. Each slot contains: Model Name, Provider, API Key"
    // "Empty slots allowed"

    // We will map over a fixed array of 3 indices
    const renderSlots = () => {
        const slots = [];
        for (let i = 0; i < MAX_MODELS; i++) {
            const model = models[i] || { id: `slot-${i}`, name: '', provider: '', apiKey: '' };

            slots.push(
                <div key={i} className="mb-6 p-4 border border-gray-800 rounded bg-black/20">
                    <div className="text-xs text-gray-500 mb-2 uppercase tracking-wider font-semibold">Model Slot {i + 1}</div>
                    <div className="space-y-3">
                        <div>
                            <label className="block text-xs text-gray-400 mb-1">Model Name</label>
                            <input
                                type="text"
                                className="w-full bg-black border border-gray-700 rounded px-3 py-2 text-sm text-white focus:border-evals-green focus:outline-none transition-colors placeholder-gray-600"
                                placeholder="e.g. GPT-4o"
                                value={model.name}
                                onChange={(e) => updateModel(i, 'name', e.target.value)}
                            />
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-xs text-gray-400 mb-1">Provider (Optional)</label>
                                <select
                                    className="w-full bg-black border border-gray-700 rounded px-3 py-2 text-sm text-white focus:border-evals-green focus:outline-none transition-colors appearance-none"
                                    value={model.provider}
                                    onChange={(e) => updateModel(i, 'provider', e.target.value)}
                                >
                                    <option value="">Select...</option>
                                    <option value="openai">OpenAI</option>
                                    <option value="anthropic">Anthropic</option>
                                </select>
                            </div>
                            <div>
                                <label className="block text-xs text-gray-400 mb-1">API Key</label>
                                <input
                                    type="password"
                                    className="w-full bg-black border border-gray-700 rounded px-3 py-2 text-sm text-white focus:border-evals-green focus:outline-none transition-colors placeholder-gray-600"
                                    placeholder="sk-..."
                                    value={model.apiKey}
                                    onChange={(e) => updateModel(i, 'apiKey', e.target.value)}
                                />
                            </div>
                        </div>
                    </div>
                </div>
            );
        }
        return slots;
    };

    return (
        <Card title="Models to Compare" description="Add up to 3 models">
            {renderSlots()}
            <div className="mt-2 text-xs text-gray-600">
                API keys are passed directly to the model provider and are not stored.
            </div>
        </Card>
    );
};
