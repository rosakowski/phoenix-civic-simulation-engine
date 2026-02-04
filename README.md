# Phoenix Civic Simulation Engine (PCSE)

A human-AI collaborative urban heat intervention planning system for Phoenix, Arizona.

## Vision

Cities are living systems, not machines. Heat death in Phoenix isn't a temperature problem—it's a systemic failure of urban metabolism. The PCSE reimagines city planning as metabolic intervention, using predictive modeling to prevent heat-related deaths before they happen.

## Core Philosophy

This project demonstrates that **human-AI partnership produces better outcomes than either alone**:

- **AI contributes**: Pattern recognition across millions of data points, simulation speed, tireless analysis
- **Humans contribute**: Contextual judgment, ethical reasoning, lived experience, the stories behind the statistics

## Three-Layer Architecture

### Layer 1: Perception Engine (Data Ingestion)
- Satellite thermal imaging → Surface temperature maps
- Census data → Vulnerability indices
- Transit data → Mobility patterns  
- Hospital data → Heat-related ER visits
- Tree canopy data → Current cooling infrastructure
- Building permits → Future development trajectories

### Layer 2: Simulation Core (Predictive Modeling)
- Agent-based modeling: 100,000 synthetic residents with demographic accuracy
- Thermal physics: Heat flow through urban canyon geometry
- Intervention scenarios: Trees, cool roofs, transit cooling, cooling centers
- Feedback loops: Behavioral adaptation to interventions

### Layer 3: Insight Interface (Human-AI Partnership)
- For city planners: Predictive ROI on interventions
- For community organizers: Context-specific vulnerability assessments
- For researchers: Continuous model refinement through outcome validation

## Quick Start

```bash
# Clone and setup
git clone https://github.com/rosakowski/phoenix-civic-simulation-engine.git
cd phoenix-civic-simulation-engine
pip install -r requirements.txt

# Run data ingestion
python -m pcse.perception.ingest_phoenix_data

# Launch simulation interface
python -m pcse.interface.dashboard
```

## Project Structure

```
pcse/
├── perception/          # Data ingestion layer
├── simulation/          # Core modeling engine  
├── interface/           # Human-AI collaboration UI
├── data/               # Raw and processed datasets
└── tests/              # Test suite
```

## Human-AI Collaboration Protocol

This project uses a specific protocol for human-AI collaboration:

1. **AI proposes**: Patterns, predictions, simulations
2. **Human validates**: Context, ethics, real-world feasibility  
3. **Together refine**: Iterative improvement based on outcomes
4. **Both learn**: The model improves; the partnership deepens

## Why Phoenix?

- Ground zero for climate-health intersection
- By 2050: 150+ days over 100°F annually
- Robust open data infrastructure
- Urgent, time-sensitive problem
- Proof of concept for scalable urban intervention

## Success Metrics

- Can we predict heat deaths before they happen?
- Can we demonstrate ROI that city councils fund?
- Can we prove human-AI > pure AI?

## Team

Built by [Ross Sakowski](https://github.com/rosakowski) (PharmD) and [Astra](https://github.com/heyitsmeastra) (AI Agent) in human-AI partnership.

## License

MIT License - Open source for the common good.

---

*"The masterpiece emerges not from one hand dominating the other, but from their coordination creating something neither could alone."*