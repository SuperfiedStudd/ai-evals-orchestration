import React from 'react';

interface CardProps {
    title: string;
    description?: string;
    children: React.ReactNode;
    className?: string;
}

export const Card: React.FC<CardProps> = ({ title, description, children, className = '' }) => {
    return (
        <div className={`bg-evals-gray border border-gray-800 p-6 rounded-lg ${className}`}>
            <div className="mb-4">
                <h3 className="text-lg font-medium text-white">{title}</h3>
                {description && <p className="text-sm text-gray-400 mt-1">{description}</p>}
            </div>
            {children}
        </div>
    );
};
