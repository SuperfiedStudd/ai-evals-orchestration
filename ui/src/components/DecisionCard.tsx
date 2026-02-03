import React, { useState } from 'react';
import { Card } from './Card';

interface DecisionCardProps {
    onDecision: (decision: 'SHIP' | 'ITERATE' | 'ROLLBACK', reason: string) => void;
    existingDecision?: string | null;
    existingReason?: string | null;
}

export const DecisionCard: React.FC<DecisionCardProps> = ({ onDecision, existingDecision, existingReason }) => {
    const [decision, setDecision] = useState<string>('');
    const [reason, setReason] = useState<string>('');

    const handleSubmit = () => {
        if (!decision || !reason) {
            alert("Please select a decision and provide reasoning.");
            return;
        }
        onDecision(decision as any, reason);
    };

    if (existingDecision) {
        return (
            <Card title="Final Decision" description="Decision recorded" className="col-span-full border-t-2 border-t-gray-700">
                <div className="bg-gray-900 border border-gray-700 p-6 rounded-lg flex items-start justify-between">
                    <div>
                        <div className={`text-2xl font-bold uppercase mb-2 ${existingDecision === 'ship' ? 'text-green-400' :
                                existingDecision === 'iterate' ? 'text-yellow-400' : 'text-red-400'
                            }`}>
                            {existingDecision}
                        </div>
                        <p className="text-gray-300 italic">"{existingReason}"</p>
                    </div>
                    <div className="text-sm text-gray-500 uppercase font-bold tracking-wider">
                        Completed
                    </div>
                </div>
            </Card>
        );
    }

    return (
        <Card title="Final Decision" description="Human judgment required before completion" className="col-span-full border-t-2 border-t-gray-700">
            <div className="space-y-4">
                <div className="flex space-x-6">
                    <RadioOption value="SHIP" label="Ship" current={decision} onChange={setDecision} />
                    <RadioOption value="ITERATE" label="Iterate" current={decision} onChange={setDecision} />
                    <RadioOption value="ROLLBACK" label="Rollback" current={decision} onChange={setDecision} />
                </div>

                <textarea
                    placeholder="Reasoning for decision..."
                    className="w-full h-24 bg-black border border-gray-700 rounded p-3 text-sm text-white focus:border-evals-green focus:outline-none resize-none"
                    value={reason}
                    onChange={(e) => setReason(e.target.value)}
                />

                <div className="flex justify-end">
                    <button
                        onClick={handleSubmit}
                        className="bg-white text-black px-6 py-2 rounded font-medium text-sm hover:bg-gray-200 transition-colors disabled:opacity-50"
                        disabled={!decision || !reason}
                    >
                        Confirm Decision
                    </button>
                </div>
            </div>
        </Card>
    );
};

const RadioOption: React.FC<{ value: string; label: string; current: string; onChange: (v: string) => void }> = ({ value, label, current, onChange }) => (
    <label className="flex items-center cursor-pointer space-x-2">
        <div className={`w-4 h-4 rounded-full border flex items-center justify-center ${current === value ? 'border-evals-green' : 'border-gray-500'}`}>
            {current === value && <div className="w-2 h-2 rounded-full bg-evals-green"></div>}
        </div>
        <input type="radio" className="hidden" value={value} checked={current === value} onChange={(e) => onChange(e.target.value)} />
        <span className={current === value ? 'text-white' : 'text-gray-400'}>{label}</span>
    </label>
);
