# Worker Agent Setup Guide

## Architecture

```
                    ┌─────────────────┐
                    │   OVERSEER      │
                    │ (Your HF Space) │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
     ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
     │ Friend's HF │  │   Your      │  │   Your      │
     │   Space     │  │  Laptop     │  │  Laptop      │
     │ (Worker 1) │  │ (Worker 2)  │  │ (Overseer)   │
     └─────────────┘  └─────────────┘  └─────────────┘
```

You have $30 credits. Here's how to use them efficiently:

---

## PART 1: Friend's HF Space (Worker 1)

Your friend deploys this on their HF account using your trained model.

### Steps for Your Friend:

1. **Create New HF Space**
   - Go to: https://huggingface.co/spaces/new
   - Name: `aegis-worker-{friendname}`
   - Type: **Space**
   - SDK: **Docker**
   - Hardware: **A10G (small)** - $3/hour
   - Visibilty: **Private** (if they want)

2. **Upload Files**
   - Upload these 3 files:
     - `hf_worker.py`
     - `requirements.txt`
     - `Dockerfile`

3. **Set Environment Variables**
   - Go to Space Settings → Variables
   - Add:
     - `HF_TOKEN` = your token (get from HF Settings → Access Tokens)
     - `WORKER_MODEL` = your trained model repo

4. **IMPORTANT: Cost Management**
   - Set a **Repository Visibility** to Private
   - After their turn, they must **Factory Reboot** the space to free resources
   - With $30 at $3/hr = ~10 hours of runtime
   - Can run in bursts: 1 hour at a time, then stop

---

## PART 2: Your Laptop (Worker 2) - Optional

If you want your laptop as a worker too:

### Setup:

```bash
# Install dependencies (if not already)
pip install -r worker_agent/requirements.txt

# Start the local worker
python worker_agent/local_worker.py
```

### Expose to Internet with ngrok:

```bash
# In a new terminal
ngrok http 7861
```

**Copy the ngrok URL** (e.g., `https://abc123.ngrok.io`) and tell your overseer about it.

---

## PART 3: Update Your Overseer

In your overseer (where you run the main model), add:

```python
from overseer_worker_client import dispatch_to_worker, set_worker_url

# After friend deploys their space, update the URL:
# set_worker_url("friend_hf", "https://friend-space.hf.space/execute")
# OR if using ngrok:
# set_worker_url("local", "https://your-ngrok-url/execute")

# To send a task:
result = await dispatch_to_worker({
    "task_id": "task_001",
    "worker_role": "general-dev",
    "instructions": "Write a hello world program in Python",
    "context": "User wants a simple script"
})
```

---

## Quick Reference

| Component | Cost | When to Use |
|-----------|------|--------------|
| Friend's HF (A10G) | ~$3/hr | When friend is online |
| Your Laptop (free) | $0 | When laptop is on |
| ngrok (free) | $0 | Tunnel to laptop |

### Total: ~$30 covers ~10 hours of HF compute

---

## Files Created

- `worker_agent/hf_worker.py` - Code for friend's HF Space
- `worker_agent/local_worker.py` - Code for your laptop
- `worker_agent/overseer_worker_client.py` - Your overseer uses this
- `worker_agent/requirements.txt` - Python dependencies
- `worker_agent/Dockerfile` - Container config

---

## Flow Example

1. **You** ask overseer a question
2. **Overseer** picks a worker (friend or laptop)
3. **Worker** processes the task with your trained model
4. **Worker** returns result to overseer
5. **Overseer** evaluates and responds

This lets you use both your friend's credits AND your laptop as workers while your HF Space acts as the overseer/manager.