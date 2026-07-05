import sys
import os
import time
import psutil

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from integration.run_full_pipeline import run_pipeline

def run_benchmarks():
    print("=== STARTING PERFORMANCE BENCHMARKS ===")
    
    process = psutil.Process(os.getpid())
    start_memory = process.memory_info().rss / (1024 * 1024)
    start_time = time.time()
    
    success = run_pipeline()
    
    end_time = time.time()
    end_memory = process.memory_info().rss / (1024 * 1024)
    
    execution_time = end_time - start_time
    mem_used = end_memory - start_memory
    
    print("\n=== BENCHMARK RESULTS ===")
    print(f"Pipeline Success: {success}")
    print(f"Total Execution Time: {execution_time:.2f} seconds")
    print(f"Peak Memory Delta: {mem_used:.2f} MB")
    print(f"Final Memory Usage: {end_memory:.2f} MB")
    
    with open("benchmark/benchmark_report.md", "w") as f:
        f.write("# Performance Benchmark Report\n\n")
        f.write(f"- **Execution Time:** {execution_time:.2f} s\n")
        f.write(f"- **Memory Used:** {mem_used:.2f} MB\n")
        
if __name__ == "__main__":
    run_benchmarks()
