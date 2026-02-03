interface SidebarProps {
    currentView: string;
    onNavigate: (view: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentView, onNavigate }) => {
    return (
        <div className="w-64 bg-black border-r border-gray-800 h-screen flex flex-col p-4 fixed left-0 top-0">
            <div className="mb-8">
                <div className="h-8 w-8 bg-evals-green rounded-sm mb-2"></div>
                <span className="font-bold text-sm tracking-tight text-gray-200">AI Model Evaluation Workspace</span>
            </div>

            <nav className="flex-1 space-y-1">
                <NavItem label="New Evaluation" id="new" active={currentView === 'new'} onClick={() => onNavigate('new')} />
                <NavItem label="Experiments" id="list" active={currentView === 'list' || currentView === 'detail'} onClick={() => onNavigate('list')} />
            </nav>

        </div>
    );
};

const NavItem: React.FC<{ label: string; active?: boolean; id: string; onClick: () => void }> = ({ label, active, onClick }) => (
    <div
        onClick={onClick}
        className={`px-3 py-2 rounded-md text-sm font-medium cursor-pointer transition-colors ${active ? 'bg-gray-900 text-evals-green' : 'text-gray-400 hover:text-gray-200 hover:bg-gray-900/50'}`}
    >
        {label}
    </div>
);
