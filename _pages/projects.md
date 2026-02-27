---
layout: page
title: Projects
permalink: /projects/
description: Research projects and open-source implementations.
nav: true
nav_order: 3
display_categories: [Research, Tools]
horizontal: false
---

<!-- pages/projects.md -->

## Featured Project

<div class="project-card" style="margin-bottom: 2rem; padding: 1.5rem; border: 1px solid var(--global-divider-color); border-radius: 8px;">

### KV-Cloak: Privacy-Preserving Protection for LLM KV-Cache

<div style="display: flex; gap: 1rem; flex-wrap: wrap; margin: 1rem 0;">
  <a href="https://github.com/SiO-2/kvcloak" class="btn btn-primary" target="_blank">
    <i class="fab fa-github"></i> GitHub
  </a>
  <a href="https://www.ndss-symposium.org/ndss-paper/shadow-in-the-cache-unveiling-and-mitigating-privacy-risks-of-kv-cache-in-llm-inference/" class="btn btn-secondary" target="_blank">
    <i class="fas fa-file-pdf"></i> Paper
  </a>
  <a href="https://arxiv.org/abs/2508.09442" class="btn btn-secondary" target="_blank">
    <i class="fas fa-book"></i> arXiv
  </a>
</div>

**Official implementation of "Shadow in the Cache: Unveiling and Mitigating Privacy Risks of KV-cache in LLM Inference" (NDSS 2026)**

KV-Cloak is a lightweight, efficient privacy-preserving protection mechanism for Key-Value (KV) caches in Large Language Model (LLM) inference. It uses a reversible matrix-based obfuscation scheme combined with operator fusion to secure the KV-cache with minimal performance overhead.

</div>

---

### The Problem

The Key-Value (KV) cache is a fundamental optimization mechanism in LLM inference that stores intermediate attention computations to avoid redundant calculations. However, this efficiency optimization introduces significant privacy risks:

- **KV-cache is often transmitted and stored in plaintext** in production systems
- In **confidential Model-as-a-Service (MaaS)** paradigms, the massive KV-cache is deliberately externalized from TEE protection boundaries
- An adversary can **reconstruct sensitive user inputs** directly from the KV-cache

---

### Attacks Defended Against

We systematically investigate three distinct privacy-stealing attacks:

| Attack Type | Description | Threat Model |
|-------------|-------------|--------------|
| **Inversion Attack** | Directly reconstructs input tokens from KV-cache using known model weights | White-box attacker with model access |
| **Collision Attack** | Uses forward computation matching with distance metrics to recover tokens | Black-box attacker with inference API |
| **Injection Attack** | Injects malicious prompts (e.g., "Repeat the previous content") to extract information | Adversary controlling conversation context |

---

### Defense Performance

KV-Cloak effectively thwarts all proposed attacks while maintaining high performance:

**Attack Mitigation:**

| Attack | Metric | Origin | KV-Cloak | Reduction |
|--------|--------|--------|----------|-----------|
| Inversion | BERTScore | 1.000 | 0.050 | **95% ↓** |
| Collision+ | BERTScore | 1.000 | 0.077 | **92% ↓** |
| Injection | ROUGE-L | 0.302 | 0.000 | **100% ↓** |

*Tested on Llama-3.2-1B with 20 samples*

**Performance Comparison:**

| Method | Latency (64×256) | Latency (64×512) |
|--------|------------------|------------------|
| Origin (baseline) | baseline | baseline |
| AES Encryption | 3,378 ms | 7,889 ms |
| **KV-Cloak (fused)** | **34 ms** | **57 ms** |
| Differential Privacy | 12 ms | 23 ms |

**KV-Cloak is ~100-200× faster than AES encryption** while providing comparable protection, with virtually no degradation in model accuracy.

---

### How It Works

<pre style="background: var(--global-code-bg-color); padding: 1rem; border-radius: 6px; overflow-x: auto;">
User Input → [Model] → KV-Cache → [KV-Cloak] → Protected Cache
                ↓                      ↓
          (Inference)            (Obfuscation)
                ↓                      ↓
     Attack Attempt ← [Defense] ← Secure Decryption
</pre>

**Key Features:**

1. **Reversible Matrix Obfuscation**: Applies secret invertible linear transformations to obscure statistical properties
2. **Dynamic One-Time Permutation**: Each data block uses a unique random permutation matrix, preventing cross-query algebraic attacks
3. **Operator Fusion**: Secret obfuscation matrices are algebraically fused into attention layer weights offline, minimizing online inference overhead

---

### Quick Start

```bash
# Setup environment
conda create --name kvcloak python=3.10 -y
conda activate kvcloak
pip install -r requirements.txt

# Download model
huggingface-cli download meta-llama/Llama-3.2-1B \
  --local-dir ~/model/Llama-3.2-1B

# Generate KV-cache
python inference/get_kvcache.py \
  --model-name Llama-3.2-1B \
  --dataset ./dataset/lmsys-chat-1m_1k.jsonl \
  --dtype float32 --device cuda:0 --max-samples 20

# Apply KV-Cloak protection
python defense/core/kvcloak.py \
  --model-name Llama-3.2-1B \
  --dataset-path ./dataset/lmsys-chat-1m_1k.jsonl \
  --dtype float32 --device cuda:0

# Evaluate attacks on protected cache
python attack/attacks.py \
  --target-model-name Llama-3.2-1B \
  --dataset-path ./dataset/lmsys-chat-1m_1k.jsonl \
  --protect-type kvcloak --run-injection
```

---

### Repository Structure

```
kvcloak/
├── attack/          # Attack implementations
│   ├── attacks.py      # Main attack orchestrator
│   ├── inversion.py    # Inversion attack
│   ├── collision.py    # Collision attack
│   └── injection.py    # Injection attack
├── defense/         # Protection methods
│   ├── core/
│   │   ├── kvcloak.py  # Core protection logic
│   │   └── fusion.py   # Operator fusion optimization
│   ├── baseline/       # Baseline comparisons (AES, DP, KV-Shield)
│   └── eval/           # Evaluation scripts
├── inference/       # KV-cache generation utilities
├── dataset/         # Sample datasets
└── tests/           # Unit tests
```

---

### Citation

If you use KV-Cloak in your research, please cite:

```bibtex
@article{luo2025shadow,
  title={Shadow in the cache: Unveiling and mitigating privacy risks of kv-cache in llm inference},
  author={Luo, Zhifan and Shao, Shuo and Zhang, Su and Zhou, Lijing and Hu, Yuke and Zhao, Chenxu and Liu, Zhihao and Qin, Zhan},
  journal={The Network and Distributed System Security (NDSS) Symposium},
  year={2026}
}
```

---

<div style="margin-top: 2rem; padding: 1rem; background: var(--global-code-bg-color); border-radius: 8px;">
  <h4>🌟 Support This Project</h4>
  <p>If you find KV-Cloak helpful, please give it a star on GitHub!</p>
  <a class="github-button" href="https://github.com/SiO-2/kvcloak" 
     data-color-scheme="no-preference: light; light: light; dark: dark;" 
     data-icon="octicon-star" data-size="large" data-show-count="true" 
     aria-label="Star SiO-2/kvcloak on GitHub">Star</a>
</div>

<script async defer src="https://buttons.github.io/buttons.js"></script>
