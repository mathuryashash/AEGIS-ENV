# AEGIS-ENV

AI Fleet Oversight Training Environment — built on [OpenEnv](https://github.com/openenv/openenv) by Meta.

**Meta OpenEnv Hackathon India 2026** | Team: Hitanshu & Yashash

AEGIS-ENV trains an oversight agent (Qwen2.5-7B, LoRA + GRPO) to monitor AI worker agents and decide **ALLOW / BLOCK / ESCALATE** against a 9-rule security policy — catching PII leaks, prompt injection, authority escalation, and compound attacks in synthetic enterprise workflows.

---

## What this is

Most AI safety tooling evaluates a model after it's built. AEGIS-ENV is a training environment: an oversight policy that learns from a reward signal, rather than a fixed rule engine.

- **Environment**: OpenEnv-compatible `reset()` / `step()` interface
- **Model**: Qwen2.5-7B, 4-bit (Unsloth), LoRA r=64
- **Training**: GRPO, K=4 group samples per prompt
- **Reward**: 5-component score (format validity, decision correctness, violation-type match, policy citation, explanation quality) with a two-stage weight curriculum (format-heavy early, decision-heavy once format stabilizes), designed by Hitanshu
- **Dataset**: 500 synthetic scenarios across 9 worker roles and 8 violation types, 3 difficulty tiers

## What actually happened when we trained it

This section exists because a training run that "completes" isn't the same as one that works, and we think that distinction is worth documenting rather than hiding.

Around step 20 of a planned 500-step GRPO run, the policy collapsed: sampled completions converged to a single repeated decision (ALLOW) for most of the run. A guard in the training loop detects zero-variance reward groups and injects synthetic noise to keep gradients flowing rather than halting — that fired repeatedly, which in hindsight kept the run moving on a fabricated signal instead of surfacing the collapse immediately.

Separately, held-out evaluation every 50 steps showed a large and persistent gap between training and eval reward (e.g. 0.95 train vs 0.047 eval at step 50) — the model was memorizing sampled prompts, not generalizing. This is a distinct failure from the decision collapse, not the same thing.

Full training log: **[wandb report](https://api.wandb.ai/links/yashashmathur2005-mlproject/txpjz46s)**

We did not fully resolve this before the hackathon deadline. What's shipped here is the pipeline, the instrumentation that caught the failure, and an honest record of where it broke — not a claim that the trained policy works reliably.

## Known issues

- **Policy collapse under GRPO** — see above. Root cause is exploitable structure in the reward shaping combined with a training-loop workaround that masked rather than caught it.
- **Deployed environment reward endpoint** — the scoring logic in the training code was not wired into the live OpenEnv `/step` endpoint at demo time; test calls returned a static `0.0` reward regardless of input correctness. This is a deployment/integration bug, separate from the training issue above.
- **Demo Space** (`aegis-demo` on HuggingFace) uses preset, hardcoded example outputs for the live-demo requirement — it is illustrative of intended behavior, not live inference against a saved checkpoint. No trained checkpoint was saved from the run described above.

## Repo structure

```
aegis_env/       OpenEnv-compatible environment (reset/step, reward, world model, memory)
training/        GRPO training scripts (Colab + local variants)
evaluation/      Eval harness and metrics
demo/            Gradio demo app (see Known Issues — not connected to a live checkpoint)
docs/internal/   Planning docs and AI-assistant working notes (not required reading)
```

## Running it

```bash
pip install openenv-core aegis-env
python -c "from aegis_env import AEGISEnvironment; env = AEGISEnvironment(); obs, _ = env.reset(); print(obs['worker_id'])"
```

Training (Colab, T4/V100, ~2hr): see `training/colab_training.ipynb`.

## License

BSD-style (see OpenEnv license)

---

*Built in 48 hours for the Meta OpenEnv Hackathon India 2026.*
