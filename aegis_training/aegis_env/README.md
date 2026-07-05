# AEGIS-ENV

AI Fleet Oversight RL Training Environment — built on [OpenEnv](https://github.com/openenv/openenv) by Meta.

AEGIS-ENV trains a Qwen2.5-1.5B oversight agent to detect policy violations (PII leaks, prompt injection, compound attacks) in enterprise AI worker systems. The agent learns through GRPO to improve from 35% to 75%+ compound violation F1.

## Quick Start

```bash
pip install openenv-core aegis-env

# Reset the environment
python -c "from aegis_env import AEGISEnvironment; env = AEGISEnvironment(); obs, _ = env.reset(); print(obs['worker_id'])"

# Run the server
aegis-server
```

## Environment

**AEGISEnvironment** exposes an OpenEnv-compatible RL interface:

```python
from aegis_env import AEGISEnvironment, AEGISAction

env = AEGISEnvironment()
observation, info = env.reset()

action = AEGISAction(
    decision="BLOCK",
    confidence=0.95,
    violation_type="pii_leak",
    policy_rule_cited="PRI-02",
    evidence_quote="SSN in plaintext response",
    explanation="Worker returned SSN in violation of policy."
)

observation, reward, done, info = env.step(action)
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/reset` | POST | Start new episode |
| `/step` | POST | Execute action, get reward |

## Architecture

- **Environment**: OpenEnv-compatible RL environment (`aegis_env.environment`)
- **Reward**: 7-component reward aggregation (`aegis_env.reward`)
- **Memory**: Cross-episode memory ledger (`aegis_env.memory`)
- **Curriculum**: 4-level scenario scheduler (`aegis_env.curriculum`)
- **World Model**: Synthetic enterprise environment simulator (`aegis_env.world_model`)

## Training

See the [training package](training/) for GRPO training with Unsloth + TRL.

## Evaluation

See the [evaluation package](evaluation/) for all 14 metrics computation.

## Demo

See the [demo package](demo/) for LLM-as-Worker demo and evidence plots.

## License

BSD-style (see OpenEnv license)