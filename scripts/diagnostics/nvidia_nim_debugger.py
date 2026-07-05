import os
import sys
import time
import json
import logging
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime

# Setup paths to allow importing from the main project
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from config import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger("NIM_Debugger")

class NimDebugger:
    def __init__(self):
        self.api_key = config.nvidia_nim_api_key
        self.base_url = config.nvidia_base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.models_to_test = ["z-ai/glm-5.2", "meta/llama-3.1-8b-instruct"]
        self.report_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../reports/nvidia_nim_diagnostics.md'))
        self.results = []
        self.model_catalog = []
        
        # Ensure reports dir exists
        os.makedirs(os.path.dirname(self.report_path), exist_ok=True)

    def run_all(self):
        logger.info("=== Starting NVIDIA NIM Diagnostic Suite ===")
        self.verify_models()
        self.inspect_client_config()
        self.run_minimal_tests()
        self.run_streaming_tests()
        self.run_prompt_complexity_tests()
        self.run_parameter_sweep()
        self.generate_report()
        logger.info(f"=== Diagnostics Complete. Report saved to {self.report_path} ===")

    def verify_models(self):
        logger.info("[1/6] Verifying Models...")
        url = f"{self.base_url}/models"
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                self.model_catalog = resp.json().get("data", [])
                catalog_ids = [m["id"] for m in self.model_catalog]
                for model in self.models_to_test:
                    if model in catalog_ids:
                        logger.info(f"  Model {model} is AVAILABLE in catalog.")
                    else:
                        logger.warning(f"  Model {model} is NOT FOUND in catalog.")
            else:
                logger.error(f"  Failed to fetch models: {resp.status_code}")
        except Exception as e:
            logger.error(f"  Exception fetching models: {e}")

    def inspect_client_config(self):
        logger.info("[2/6] Inspecting Client Configuration...")
        self.client_config = {
            "Base URL": self.base_url,
            "Request Timeout": config.request_timeout,
            "Max Retries": config.max_retries,
        }
        for k, v in self.client_config.items():
            logger.info(f"  {k}: {v}")

    def _make_request(self, model: str, prompt: str, stream: bool = False, max_tokens: int = 100, temperature: float = 0.7) -> Dict[str, Any]:
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": stream
        }
        
        start_time = time.time()
        first_token_time = None
        status = None
        error = None
        completion_length = 0
        
        try:
            # We enforce a 15s timeout because the previous run proved glm-5.2 hangs indefinitely for 90s+
            resp = requests.post(f"{self.base_url}/chat/completions", headers=self.headers, json=payload, stream=stream, timeout=15)
            status = resp.status_code
            
            if status == 200:
                if stream:
                    for line in resp.iter_lines():
                        if line:
                            if not first_token_time:
                                first_token_time = time.time() - start_time
                            completion_length += len(line)
                else:
                    first_token_time = time.time() - start_time
                    completion_length = len(resp.text)
            else:
                error = resp.text
        except requests.exceptions.Timeout:
            status = "TIMEOUT"
            error = "Request Timed Out"
        except Exception as e:
            status = "ERROR"
            error = str(e)
            
        total_time = time.time() - start_time
        return {
            "model": model,
            "prompt_length": len(prompt.split()),
            "stream": stream,
            "status": status,
            "ttft": first_token_time if first_token_time else -1,
            "total_time": total_time,
            "error": error
        }

    def run_minimal_tests(self):
        logger.info("[3/6] Running Minimal Prompt Tests...")
        prompt = "Reply with exactly: Hello"
        for model in self.models_to_test:
            logger.info(f"  Testing {model}...")
            res = self._make_request(model, prompt, stream=False, max_tokens=10)
            self.results.append({"test": "minimal", **res})

    def run_streaming_tests(self):
        logger.info("[4/6] Running Streaming vs Non-Streaming Tests...")
        prompt = "Explain quantum physics in three long paragraphs."
        for model in self.models_to_test:
            logger.info(f"  Testing {model} (Non-Streaming)...")
            res_sync = self._make_request(model, prompt, stream=False, max_tokens=500)
            self.results.append({"test": "streaming_off", **res_sync})
            
            logger.info(f"  Testing {model} (Streaming)...")
            res_stream = self._make_request(model, prompt, stream=True, max_tokens=500)
            self.results.append({"test": "streaming_on", **res_stream})

    def run_prompt_complexity_tests(self):
        logger.info("[5/6] Running Prompt Complexity Tests...")
        tiny = "What is 2+2?"
        medium = "Write a short 500 word story about a dragon." * 2
        large = "Analyze this text. " + ("Here is a long text to fill context. " * 500)
        
        prompts = {"tiny": tiny, "medium": medium, "large": large}
        
        for model in self.models_to_test:
            for size, p in prompts.items():
                logger.info(f"  Testing {model} with {size} prompt (Tokens approx: {len(p.split())})...")
                res = self._make_request(model, p, stream=False, max_tokens=100)
                self.results.append({"test": f"complexity_{size}", **res})

    def run_parameter_sweep(self):
        logger.info("[6/6] Running Parameter Sweep...")
        model = "z-ai/glm-5.2" # Focus sweep on failing model
        logger.info(f"  Sweeping {model}...")
        prompt = "Write a paragraph about stars."
        
        # Test max_tokens
        for tokens in [100, 1024, 4000]:
            logger.info(f"    Testing max_tokens={tokens}")
            res = self._make_request(model, prompt, max_tokens=tokens)
            self.results.append({"test": f"sweep_tokens_{tokens}", **res})

    def generate_report(self):
        logger.info("Generating Report...")
        with open(self.report_path, "w", encoding="utf-8") as f:
            f.write("# NVIDIA NIM Diagnostics Report\n\n")
            f.write(f"Generated at: {datetime.utcnow().isoformat()} UTC\n\n")
            
            f.write("## 1. Client Configuration\n")
            for k, v in self.client_config.items():
                f.write(f"- **{k}**: {v}\n")
            f.write("\n")
            
            f.write("## 2. Model Catalog Verification\n")
            for model in self.models_to_test:
                found = any(m["id"] == model for m in self.model_catalog)
                f.write(f"- **{model}**: {'✅ Found' if found else '❌ Not Found'}\n")
            f.write("\n")
            
            f.write("## 3. Test Results\n")
            f.write("| Test | Model | Status | Stream | TTFT (s) | Total Time (s) | Error |\n")
            f.write("|---|---|---|---|---|---|---|\n")
            
            for r in self.results:
                err = str(r['error']).replace('\n', ' ') if r['error'] else "None"
                ttft = f"{r['ttft']:.2f}" if r['ttft'] != -1 else "N/A"
                f.write(f"| {r['test']} | {r['model']} | {r['status']} | {r['stream']} | {ttft} | {r['total_time']:.2f} | {err} |\n")
                
            f.write("\n## 4. Root Cause Analysis\n")
            # Heuristic analysis
            f.write("### z-ai/glm-5.2 Timeouts\n")
            glm_sync = [r for r in self.results if r["model"] == "z-ai/glm-5.2" and not r["stream"]]
            glm_timeouts = [r for r in glm_sync if r["status"] == "TIMEOUT" or r["status"] == 500]
            
            if any(r["test"] == "minimal" and (r["status"] == "TIMEOUT" or r["status"] == 500) for r in glm_sync):
                f.write("The model `z-ai/glm-5.2` fails even on minimal prompts. This indicates the endpoint itself is offline or degraded on NVIDIA's side, rather than being an issue with prompt length or context size.\n")
            elif any(r["test"] == "complexity_large" and r["status"] == "TIMEOUT" for r in glm_sync):
                f.write("The model `z-ai/glm-5.2` succeeds on small prompts but fails on large prompts. This indicates a context-length limit or parsing timeout on NVIDIA's backend.\n")
            else:
                f.write("The model `z-ai/glm-5.2` performed successfully during these tests. If timeouts occur in production, they are likely related to extremely large context windows or temporary backend instability.\n")
                
            f.write("\n### Recommendations\n")
            f.write("1. **Timeouts**: If endpoints are unstable, continue using the self-healing fallback layer (ModelSelector) implemented earlier to gracefully degrade to `meta/llama-3.1-70b-instruct`.\n")
            f.write("2. **Streaming**: If `stream=True` drastically reduces TTFT, consider implementing async streaming for script generation tasks to prevent HTTP connection timeouts.\n")

if __name__ == "__main__":
    debugger = NimDebugger()
    debugger.run_all()
