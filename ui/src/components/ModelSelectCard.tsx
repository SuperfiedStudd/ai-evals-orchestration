import React from 'react';
import { Card } from './Card';

interface ModelSelectCardProps {
    selectedModels: string[];
    onChange: (models: string[]) => void;
}

const MODELS = ['GPT-4o', 'Claude 3.5 Sonnet', 'Gemini 1.5 Pro'];

export const ModelSelectCard: React.FC<ModelSelectCardProps> = ({ selectedModels, onChange }) => {
    const toggleModel = (model: string) => {
        if (selectedModels.includes(model)) {
            onChange(selectedModels.filter(m => m !== model));
        } else {
            if (selectedModels.length < 3) {
                onChange([...selectedModels, model]);
            }
        }
    };

    return (
        <Card title="Models to Compare" description="Choose up to 3 LLMs">
            <div className="space-y-3">
                {MODELS.map(model => (
                    <label key={model} className="flex items-center space-x-3 cursor-pointer group">
                        <input
                            type="checkbox"
                            className="hidden"
                            checked={selectedModels.includes(model)}
                            onChange={() => toggleModel(model)}
                        />
                        <div className={`w-5 h-5 border rounded flex items-center justify-center transition-colors ${selectedModels.includes(model) ? 'bg-evals-green border-evals-green' : 'border-gray-600 group-hover:border-gray-400'}`}>
                            {selectedModels.includes(model) && (
                                <svg className="w-3 h-3 text-black" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                                </svg>
                            )}
                        </div>
                        <span className={selectedModels.includes(model) ? 'text-white' : 'text-gray-400'}>{model}</span>
                    </label>
                ))}
            </div>
            <div className="mt-4 text-xs text-gray-500">Max 3 models</div>
        </Card>
    );
};
