import matplotlib.pyplot as plt
import time
import random
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

from hospital_finder import BASE_GRAPH, nodes_coord
from helper_function import dijkstra, astar_search

def run_comparison_benchmark():
    """
    Chạy so sánh tốc độ giữa Dijkstra và A*
    """
    print(">>> Starting algorithm comparison (Dijkstra vs A*)...") 
 
    sizes = [10, 20, 30, 40, 50] 
    dijkstra_times = []
    astar_times = []

    all_nodes = list(BASE_GRAPH.keys())
    
    for n in sizes:
        print(f"   -> Processing batch size: {n}...")

        start_time = time.perf_counter()
        for _ in range(n):
            start_node = random.choice(all_nodes)
            dijkstra(BASE_GRAPH, start_node)
        avg_time_d = (time.perf_counter() - start_time)
        dijkstra_times.append(avg_time_d)
        start_time = time.perf_counter()
        for _ in range(n):
            s = random.choice(all_nodes)
            e = random.choice(all_nodes)
            if s != e:
                astar_search(BASE_GRAPH, s, e, nodes_coord)
        avg_time_a = (time.perf_counter() - start_time)
        astar_times.append(avg_time_a)

    plt.figure(figsize=(10, 6))
    plt.plot(sizes, dijkstra_times, marker='o', label='Dijkstra (Full Scan)', 
             color='#e74c3c', linewidth=2, linestyle='-')
    plt.plot(sizes, astar_times, marker='s', label='A* Search (Heuristic)', 
             color='#2ecc71', linewidth=2, linestyle='--')
    
    plt.xlabel('Number of Requests', fontweight='bold')
    plt.ylabel('Total Execution Time (seconds)', fontweight='bold')
    plt.title('PERFORMANCE COMPARISON: DIJKSTRA vs A*', fontweight='bold', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    
    output_file = 'algo_comparison.png'
    plt.savefig(output_file, dpi=300)
    print(f"[OK] Success! Chart saved to: {output_file}")

if __name__ == "__main__":
    try:
        run_comparison_benchmark()
    except Exception as e:
        print(f"Error: {e}")