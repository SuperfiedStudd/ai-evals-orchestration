import React, { useState } from 'react';
import { Card } from './Card';

interface UploadCardProps {
    onUpload: (data: { type: 'audio' | 'text', file?: File, text?: string }) => void;
}

export const UploadCard: React.FC<UploadCardProps> = ({ onUpload }) => {
    const [activeTab, setActiveTab] = useState<'audio' | 'text'>('audio');
    const [file, setFile] = useState<File | null>(null);
    const [text, setText] = useState<string>('');

    const handleFile = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files?.[0]) {
            const f = e.target.files[0];
            setFile(f);
            onUpload({ type: 'audio', file: f });
        }
    };

    const handleText = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        const val = e.target.value;
        setText(val);
        // Always pass text update
        onUpload({ type: 'text', text: val });
    };

    return (
        <Card title="Upload Content" description="Upload audio or paste transcript to evaluate editing quality">
            <div className="flex space-x-4 mb-4 border-b border-gray-800">
                <button
                    className={`pb-2 text-sm font-medium transition-colors ${activeTab === 'audio' ? 'text-evals-green border-b-2 border-evals-green' : 'text-gray-500 hover:text-white'}`}
                    onClick={() => { setActiveTab('audio'); setFile(null); onUpload({ type: 'audio', file: undefined }); }}
                >
                    Audio File
                </button>
                <button
                    className={`pb-2 text-sm font-medium transition-colors ${activeTab === 'text' ? 'text-evals-green border-b-2 border-evals-green' : 'text-gray-500 hover:text-white'}`}
                    onClick={() => { setActiveTab('text'); setText(''); onUpload({ type: 'text', text: '' }); }}
                >
                    Transcript Text
                </button>
            </div>

            {activeTab === 'audio' ? (
                <div className="border-2 border-dashed border-gray-700 rounded-md p-8 text-center hover:border-evals-green transition-colors cursor-pointer relative">
                    <input
                        type="file"
                        accept=".mp3,.wav"
                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                        onChange={handleFile}
                    />
                    {file ? (
                        <div className="text-evals-green font-mono text-sm">{file.name}</div>
                    ) : (
                        <div className="text-gray-500 text-sm">
                            <span className="block text-xl mb-2">⬇️</span>
                            Click or drag audio file (.mp3, .wav)
                        </div>
                    )}
                    <p className="mt-4 text-xs text-gray-600">Audio is transcribed before evaluation to ensure fair comparison.</p>
                </div>
            ) : (
                <div className="space-y-2">
                    <textarea
                        className="w-full h-32 bg-black border border-gray-700 rounded p-3 text-sm text-white focus:border-evals-green focus:outline-none resize-none placeholder-gray-600"
                        placeholder="Paste transcript here..."
                        value={text}
                        onChange={handleText}
                    />
                </div>
            )}
        </Card>
    );
};
