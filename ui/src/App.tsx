import { useState, useEffect, useRef } from 'react';
import { Sidebar } from './components/Sidebar';
import { UploadCard } from './components/UploadCard';
import { ModelConfigCard, type ModelConfig } from './components/ModelConfigCard';
import { RunEvalCard } from './components/RunEvalCard';
import { ResultsCard } from './components/ResultsCard';
import { DecisionCard } from './components/DecisionCard';
import { ExperimentsList } from './components/ExperimentsList';
import { ExperimentDetailView } from './components/ExperimentDetailView';

const API_BASE = 'http://localhost:8000/v1';

function App() {
  const [currentView, setCurrentView] = useState('new'); // 'new', 'list', 'detail'
  const [selectedExperimentId, setSelectedExperimentId] = useState<string | null>(null);

  const [inputType, setInputType] = useState<'audio' | 'text' | null>(null);
  const [uploadData, setUploadData] = useState<{ file?: File; text?: string }>({});

  // Initialize with 3 empty slots
  const [models, setModels] = useState<ModelConfig[]>([
    { id: 'slot-0', name: '', provider: '', apiKey: '' },
    { id: 'slot-1', name: '', provider: '', apiKey: '' },
    { id: 'slot-2', name: '', provider: '', apiKey: '' },
  ]);

  const [loading, setLoading] = useState(false);
  const [loadingText, setLoadingText] = useState('Running Evaluation...');
  const [results, setResults] = useState<any[] | null>(null);
  const [experimentId, setExperimentId] = useState<string | null>(null);
  const [experimentData, setExperimentData] = useState<any | null>(null);

  // Polling ref
  const pollIntervalRef = useRef<number | null>(null);

  const handleNavigate = (view: string) => {
    setCurrentView(view);
    if (view !== 'detail') setSelectedExperimentId(null);
  };

  const handleSelectExperiment = (id: string) => {
    setSelectedExperimentId(id);
    setCurrentView('detail');
  };

  const handleUpload = (data: { type: 'audio' | 'text', file?: File, text?: string }) => {
    setInputType(data.type);
    setUploadData({ file: data.file, text: data.text });
  };

  const handleRunEval = async () => {
    setLoading(true);
    setLoadingText('Starting Experiment...');
    setResults(null);
    setExperimentData(null);

    const validModels = models.filter(m => m.name.trim() !== '');
    if (validModels.length === 0) {
      alert("Please configure at least one model.");
      setLoading(false);
      return;
    }

    try {
      const formData = new FormData();
      if (uploadData.file) {
        formData.append('file', uploadData.file);
      } else if (uploadData.text) {
        formData.append('text', uploadData.text);
      } else {
        alert("No content to evaluate.");
        setLoading(false);
        return;
      }

      // Format models list for backend
      // Backend expects list of {name, provider, api_key}
      // UI models have {name, provider, apiKey}
      const modelsPayload = validModels.map(m => ({
        name: m.name,
        provider: m.provider || "openai", // Default fallback
        apiKey: m.apiKey
      }));
      formData.append('models', JSON.stringify(modelsPayload));

      const response = await fetch(`${API_BASE}/experiment`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Failed to start experiment: ${response.statusText}`);
      }

      const data = await response.json();
      setExperimentId(data.experiment_id);
      setLoadingText('Running... (Transcribing & Evaluating)');

      // Start polling
      startPolling(data.experiment_id);

    } catch (e: any) {
      console.error(e);
      alert(e.message);
      setLoading(false);
    }
  };

  const startPolling = (id: string) => {
    if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);

    pollIntervalRef.current = window.setInterval(async () => {
      try {
        const res = await fetch(`${API_BASE}/experiment/${id}`);
        if (!res.ok) return;

        const data = await res.json();
        // console.log(`Poll Status [${id}]:`, data); 

        // Update experiment data fully
        setExperimentData({
          status: data.status,
          decision: data.decision || null, // Backend might not send if null
          decision_reason: data.decision_reason || null
        });

        const status = data.status?.toLowerCase() || 'unknown';

        // Always update results if present (partial or full)
        if (data.results && data.results.length > 0) {
          const uiResults = data.results.map((r: any) => {
            const getScore = (name: string) => r.scores?.find((s: any) => s.metric_name === name)?.score || 0;
            const editQuality = getScore('edit_quality');
            const readyScore = getScore('publish_ready');

            return {
              model: r.model || "Unknown Model",
              effort: editQuality > 3 ? 'Low' : 'Medium',
              quality: editQuality >= 4 ? 'High' : (editQuality >= 3 ? 'Medium' : 'Low'),
              ready: readyScore >= 4 ? 'Yes' : 'No',
              cost: r.cost,
              latency: r.latency,
              isWinner: r.model === data.recommendation
            };
          });
          setResults(uiResults);
        }

        if (status === 'failed') {
          clearInterval(pollIntervalRef.current!);
          setLoading(false);
          // Verbose debug alert
          const errorMsg = data.error_log || "No error_log in response";
          alert(`Experiment Failed!\nStatus: ${status}\nError: ${errorMsg}\n\nFull Response:\n${JSON.stringify(data, null, 2)}`);
        }
        else if (status === 'complete' || status === 'awaiting_decision') {
          // Terminal state logic
          setLoading(false);
          clearInterval(pollIntervalRef.current!);
        }
        else {
          // Still running (e.g. "running")
          setLoadingText(`Status: ${data.status}...`);
        }

      } catch (e) {
        console.error("Polling error", e);
      }
    }, 2000);
  };

  const handleDecision = async (decision: 'SHIP' | 'ITERATE' | 'ROLLBACK', reason: string) => {
    if (!experimentId) {
      // Debugging: why is ID missing?
      console.error("No experimentId found when submitting decision.");
      alert("System Error: No Experiment ID found. Please verify the experiment started correctly.");
      return;
    }
    try {
      const res = await fetch(`${API_BASE}/decision`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          experiment_id: experimentId,
          decision: decision,
          decision_reason: reason
        })
      });
      if (res.ok) {
        alert("Decision Recorded. Experiment Complete.");
        // Optimistic update or refresh
        setExperimentData(prev => prev ? ({ ...prev, decision, decision_reason: reason }) : null);
      }
    } catch (e) {
      console.error(e);
    }
  };

  // Ready if file uploaded AND at least one model has a name
  const isReady = (!!uploadData.file || (!!uploadData.text && uploadData.text.length > 0)) && models.some(m => m.name.trim() !== '');

  const renderContent = () => {
    if (currentView === 'list') {
      return <ExperimentsList onSelect={handleSelectExperiment} />;
    }
    if (currentView === 'detail' && selectedExperimentId) {
      return <ExperimentDetailView experimentId={selectedExperimentId} onBack={() => setCurrentView('list')} />;
    }

    // Default: 'new'
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 max-w-7xl animate-fade-in">
        {/* Row 1: Setup */}
        <div className="space-y-6">
          <UploadCard onUpload={handleUpload} />
          <RunEvalCard ready={isReady} onRun={handleRunEval} loading={loading} loadingText={loadingText} />
        </div>

        <div className="md:col-span-1 xl:col-span-2">
          <ModelConfigCard models={models} onChange={setModels} />
        </div>

        {/* Row 3: Results */}
        {results && (
          <>
            <ResultsCard results={results} />
            <DecisionCard
              onDecision={handleDecision}
              existingDecision={experimentData?.decision}
              existingReason={experimentData?.decision_reason}
            />
          </>
        )}
      </div>
    );
  };

  return (
    <div className="flex bg-black text-gray-300 min-h-screen font-sans">
      <Sidebar currentView={currentView} onNavigate={handleNavigate} />

      <main className="ml-64 flex-1 p-12 overflow-y-auto">
        <header className="mb-12">
          {currentView === 'new' && (
            <>
              <h1 className="text-3xl font-bold text-white tracking-tight">AI Model Evaluation Workspace</h1>
              <p className="text-gray-500 mt-2">Compare editing quality across LLMs before shipping</p>
            </>
          )}
        </header>

        {renderContent()}
      </main>
    </div>
  );
}

export default App;
