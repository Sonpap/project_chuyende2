import time
import tracemalloc
import pandas as pd
import random
import sys
import os
import copy

sys.setrecursionlimit(3000)

if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from hospital_finder import *
    from hospital_finder import _hospital_coord_lock, _graph_lock
except ImportError:
    sys.path.append('..')
    from hospital_finder import *
    from hospital_finder import _hospital_coord_lock, _graph_lock

class BlockPrint:
    """Block all print statements"""
    def __enter__(self):
        self._original_stdout = sys.stdout
        self._stderr = sys.stderr
        sys.stdout = open(os.devnull, 'w', encoding='utf-8')
        sys.stderr = open(os.devnull, 'w', encoding='utf-8')
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stderr.close()
        sys.stdout = self._original_stdout
        sys.stderr = self._stderr

def run_accuracy_test(num_trials=8):
    """
    Test độ chính xác của hệ thống
    Returns: (filter_accuracy%, pathfinding_accuracy%)
    """
    print(f"--- ACCURACY TEST ({num_trials} samples) ---")
    success_filter = 0
    success_path = 0
    symptom_list = ['Da khoa', 'Tim mach', 'Nha khoa', 'Mat']

    with _hospital_coord_lock:
        original_coord = copy.deepcopy(hospital_coord)
    with _graph_lock:
        original_graph = copy.deepcopy(G)
    
    with BlockPrint():
        for i in range(num_trials):
            try:
                reset_graph()
                generate_hospital_dict(random.choice(symptom_list))
                if len(hospital_list) > 0: 
                    success_filter += 1
            except Exception as e:
                pass

            if i % 2 == 0:
                time.sleep(0.05)

            try:
                start_node = random.choice(nodes_list)
                loc_user = get_user_location(start_node)
                if loc_user:
                    closest = find_closest_hospital(loc_user)
                    if closest:
                        reset_graph()
                        create_user_edge(loc_user)
                        dijkstra(G, 'Loc User')
                        path = get_shortest_path('Loc User', closest[0])
                        if path: 
                            success_path += 1
            except Exception as e:
                pass

    print("-> Restoring system state...")
    with _hospital_coord_lock:
        hospital_coord.clear()
        hospital_coord.update(original_coord)
    with _graph_lock:
        G.clear()
        G.update(original_graph)
    
    filter_acc = (success_filter / num_trials) * 100
    path_acc = (success_path / num_trials) * 100
    
    return filter_acc, path_acc

def run_benchmark_suite():
    """
    Chạy bộ test đánh giá hiệu năng
    Returns: tên file CSV chứa kết quả
    """
    results = []
    sizes = [5, 10, 15]
    
    print("--- BENCHMARK STARTING ---")

    with _hospital_coord_lock:
        backup_coord = copy.deepcopy(hospital_coord)
    with _graph_lock:
        backup_graph = copy.deepcopy(G)

    for i, size in enumerate(sizes):
        print(f"Progress: {i+1}/{len(sizes)} (size={size})")
        time.sleep(0.1)  
        
        tracemalloc.start()
        start_time = time.perf_counter()
        
        with BlockPrint():
            for j in range(size):
                try:
                    loc = random.choice(nodes_list)
                    _ = get_user_location(loc)

                    if j % 3 == 0:
                        time.sleep(0.05)
                except: 
                    pass
        
        end_time = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        results.append({
            "Type": "Performance", 
            "Input_Size": size,
            "Time": end_time - start_time,
            "Memory": max(peak / 1024, 0.1),
            "Accuracy_Filter": 0, 
            "Accuracy_Path": 0
        })

        reset_graph()

    print("Running accuracy test...")
    acc_f, acc_p = run_accuracy_test(num_trials=8)
    
    results.append({
        "Type": "Accuracy", 
        "Input_Size": 0, 
        "Time": 0, 
        "Memory": 0,
        "Accuracy_Filter": acc_f, 
        "Accuracy_Path": acc_p
    })

    with _hospital_coord_lock:
        hospital_coord.clear()
        hospital_coord.update(backup_coord)
    with _graph_lock:
        G.clear()
        G.update(backup_graph)

    df = pd.DataFrame(results)
    csv_name = "system_evaluation_data.csv"
    df.to_csv(csv_name, index=False, encoding='utf-8-sig')
    
    print("[OK] Benchmark completed!")  
    return csv_name

if __name__ == "__main__":
    try:
        csv_file = run_benchmark_suite()
        print(f"Results saved to: {csv_file}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()