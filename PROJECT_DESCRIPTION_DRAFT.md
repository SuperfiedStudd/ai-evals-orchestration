## **Target Project: AI Evals & Experimentation Platform**
*Designed to demonstrate core competencies for the Descript "Product Manager, AI Models" role: Evals Strategy, Infrastructure, and Cost/Quality Tradeoffs.*

### **AI Evals & Experimentation Platform for Creative AI** | [Role] | [Dates]
*   **Eval Strategy & Infrastructure**: Built a production-grade evaluation harness to benchmark LLM performance on creative editing tasks. Orchestrated side-by-side comparisons of **GPT-4o** and **Claude 3 Haiku**, enabling data-driven "build vs. buy" decisions based on quality, latency, and cost per token.
*   **Human-in-the-Loop Workflow**: Designed and implemented a "Ship/Iterate/Rollback" decision workflow, closing the loop between automated heuristic scores (structure, length) and qualitative human expert review. This reflects the exact "Evals & Quality" responsibilities in the Descript JD.
*   **Technical Product Management**: Managed the full lifecycle of the internal platform from schema design (Supabase) to frontend UX (React), creating a "single pane of glass" for research teams to visualize model tradeoffs.
*   **Cost & Latency Optimization**: Instrumented granular telemetry to track inference costs and latency, identifying that Claude 3 Haiku provided 90% of the quality at 5% of the cost for specific editing tasks, directly informing product roadmap decisions.
*   **Resilient Architecture**: Architected an asynchronous orchestration engine using FastAPI and background tasks to handle long-running model inference without blocking the user interface, demonstrating understanding of "Production ML Infrastructure."
