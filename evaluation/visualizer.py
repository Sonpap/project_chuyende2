import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

try:
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'DejaVu Sans']
except:
    pass

plt.rcParams['axes.unicode_minus'] = False  

def draw_all_charts(csv_file):
    """
    Vẽ 3 biểu đồ từ dữ liệu CSV
    Args:
        csv_file: đường dẫn file CSV chứa kết quả benchmark
    """
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"File {csv_file} khong ton tai!")

    df = pd.read_csv(csv_file)

    perf_data = df[df['Type'] == 'Performance']
    acc_data = df[df['Type'] == 'Accuracy']
    
    if perf_data.empty:
        raise ValueError("Khong co du lieu Performance trong file CSV!")

    draw_chart_1_time(perf_data)
    draw_chart_2_memory(perf_data)
    
    if not acc_data.empty:
        draw_chart_3_accuracy(acc_data)
    else:
        print("Warning: Khong co du lieu Accuracy")
    
    print("Da xuat thanh cong 3 bieu do!")

def draw_chart_1_time(perf_data):
    """
    Biểu đồ 1: Time Performance (Line Chart)
    """
    plt.figure(figsize=(10, 6))
    
    sizes = perf_data['Input_Size'].values
    times = perf_data['Time'].values
    
    plt.plot(sizes, times, marker='o', linewidth=2, markersize=8, 
             color='#3498db', label='Execution Time')

    for i, (x, y) in enumerate(zip(sizes, times)):
        plt.text(x, y + 0.001, f'{y:.4f}s', ha='center', va='bottom', fontsize=9)
    
    plt.xlabel('Input Size (Number of Operations)', fontsize=12, fontweight='bold')
    plt.ylabel('Time (seconds)', fontsize=12, fontweight='bold')
    plt.title('Chart 1: System Performance - Execution Time', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend(fontsize=10)
    plt.tight_layout()
    
    plt.savefig('Chart_1_Time_Performance.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("[OK] Saved: Chart_1_Time_Performance.png")

def draw_chart_2_memory(perf_data):
    """
    Biểu đồ 2: Memory Usage (Bar Chart)
    """
    plt.figure(figsize=(10, 6))
    
    sizes = perf_data['Input_Size'].values
    memory = perf_data['Memory'].values
    
    bars = plt.bar(sizes, memory, color='#e74c3c', alpha=0.7, edgecolor='black', linewidth=1.2)

    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f} KB', ha='center', va='bottom', fontsize=10)
    
    plt.xlabel('Input Size (Number of Operations)', fontsize=12, fontweight='bold')
    plt.ylabel('Memory Usage (KB)', fontsize=12, fontweight='bold')
    plt.title('Chart 2: System Performance - Memory Consumption', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, linestyle='--', axis='y')
    plt.tight_layout()
    
    plt.savefig('Chart_2_Memory_Usage.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("[OK] Saved: Chart_2_Memory_Usage.png")

def draw_chart_3_accuracy(acc_data):
    """
    Biểu đồ 3: Accuracy Metrics (Horizontal Bar Chart)
    """
    plt.figure(figsize=(10, 6))
 
    acc_filter = acc_data['Accuracy_Filter'].values[0]
    acc_path = acc_data['Accuracy_Path'].values[0]
    
    categories = ['Hospital Filter\nAccuracy', 'Pathfinding\nAccuracy']
    values = [acc_filter, acc_path]
    colors = ['#2ecc71', '#9b59b6']
    
    bars = plt.barh(categories, values, color=colors, alpha=0.8, edgecolor='black', linewidth=1.2)

    for i, (bar, val) in enumerate(zip(bars, values)):
        plt.text(val + 1, i, f'{val:.1f}%', va='center', fontsize=11, fontweight='bold')
    
    plt.xlabel('Accuracy (%)', fontsize=12, fontweight='bold')
    plt.title('Chart 3: System Accuracy Evaluation', fontsize=14, fontweight='bold')
    plt.xlim(0, 110)
    plt.grid(True, alpha=0.3, linestyle='--', axis='x')
    plt.tight_layout()
    
    plt.savefig('Chart_3_Accuracy.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("[OK] Saved: Chart_3_Accuracy.png")

def draw_combined_chart(csv_file):
    """
    BONUS: Biểu đồ tổng hợp 3 trong 1
    """
    if not os.path.exists(csv_file):
        return
    
    df = pd.read_csv(csv_file)
    perf_data = df[df['Type'] == 'Performance']
    acc_data = df[df['Type'] == 'Accuracy']
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    ax1 = axes[0]
    sizes = perf_data['Input_Size'].values
    times = perf_data['Time'].values
    ax1.plot(sizes, times, marker='o', linewidth=2, markersize=8, color='#3498db')
    ax1.set_xlabel('Input Size', fontweight='bold')
    ax1.set_ylabel('Time (s)', fontweight='bold')
    ax1.set_title('Execution Time', fontweight='bold')
    ax1.grid(True, alpha=0.3)
 
    ax2 = axes[1]
    memory = perf_data['Memory'].values
    ax2.bar(sizes, memory, color='#e74c3c', alpha=0.7)
    ax2.set_xlabel('Input Size', fontweight='bold')
    ax2.set_ylabel('Memory (KB)', fontweight='bold')
    ax2.set_title('Memory Usage', fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')

    if not acc_data.empty:
        ax3 = axes[2]
        acc_filter = acc_data['Accuracy_Filter'].values[0]
        acc_path = acc_data['Accuracy_Path'].values[0]
        categories = ['Filter', 'Path']
        values = [acc_filter, acc_path]
        colors = ['#2ecc71', '#9b59b6']
        ax3.barh(categories, values, color=colors, alpha=0.8)
        ax3.set_xlabel('Accuracy (%)', fontweight='bold')
        ax3.set_title('System Accuracy', fontweight='bold')
        ax3.set_xlim(0, 110)
        ax3.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    plt.savefig('Chart_Combined_All.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("[OK] Saved: Chart_Combined_All.png")

if __name__ == "__main__":
    try:
        csv_file = "system_evaluation_data.csv"
        if os.path.exists(csv_file):
            draw_all_charts(csv_file)
            draw_combined_chart(csv_file)
            print("\n[SUCCESS] Tat ca bieu do da duoc tao!")
        else:
            print(f"[ERROR] Khong tim thay file: {csv_file}")
            print("Vui long chay benchmark truoc!")
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()