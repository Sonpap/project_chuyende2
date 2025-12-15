from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import tkinter as tk
import os
import threading
import time
from helper_function import *
from hospital_finder import * 
from hospital_finder import nodes_list, reset_graph
from evaluation import benchmark_engine
from evaluation import visualizer

DISTRICTS_DATA = {
    'Tat ca': nodes_list, 
    'Quan Hai Chau': ['Bao tang Cham', 'Cau Rong', 'Cho Con', 'Cho Han', 'Cong vien APEC', 'Dai hoc Duy Tan', 'Khach san Hilton', 'Khach san Novotel', 'Nha hat Trung Vuong', 'San Bay Da Nang', 'San van dong Chi Lang', 'Trung tam Hanh chinh', 'Ga Da Nang'],
    'Quan Thanh Khe': ['Cong vien 29/3', 'Dai hoc The Duc The Thao', 'Nga Ba Hue', 'Sieu thi Co.op Mart', 'Tuong dai Me Nhu'],
    'Quan Lien Chieu': ['Bai tam Xuan Thieu', 'Ben xe Trung Tam', 'Dai hoc Bach Khoa', 'Dai hoc Su Pham', 'Khu Cong Nghiep Hoa Khanh'],
    'Quan Son Tra': ['Bien My Khe', 'Cau Song Han', 'Cau Thuan Phuoc', 'Cau Tinh Yeu', 'Chua Linh Ung (Son Tra)', 'Cong vien Bien Dong', 'InterContinental Resort', 'Khach san Muong Thanh', 'Vincom Ngo Quyen'],
    'Quan Ngu Hanh Son': ['Cong vien Chau A (Asia Park)', 'Dai hoc Kinh Te', 'FPT City', 'Helio Center', 'Lotte Mart', 'Ngu Hanh Son (Danh thang)', 'Resort Furama'],
    'Quan Cam Le': ['Cau Rong (Duoi cau phia Dong)', 'Trung tam Hoi cho Trien lam']
}

root = Tk()
root.geometry("1300x820")
root.title("Hệ Thống Tìm Kiếm Bệnh Viện Đà Nẵng - Thông Minh")
root['bg'] = '#E8F4F8'

namevalue = StringVar()
agevalue = StringVar()
gendervalue = StringVar()
symptomvalue = StringVar()
districtvalue = StringVar() 
locationvalue = StringVar()
symptom_list = ['Da khoa', 'Tim mach', 'Nha khoa', 'Mat', 'Phu san', 'Chan thuong chinh hinh', 'Than kinh', 'Noi tiet', 'Tieu hoa', 'Da lieu', 'Ung buou']

is_processing = False

def toggle_gui_state(state):
    """Bật/Tắt toàn bộ giao diện"""
    widgets = [name_entry, age_entry, gender_combo, symptom_combo, 
               district_combo, location_combo, btn_find, btn_emergency, 
               btn_benchmark, btn_visualize]
    for w in widgets:
        try:
            w.config(state=state)
        except: 
            pass

def user_entry_print():
    """In thông tin bệnh nhân"""
    txtarea.delete('1.0', END) 
    txtarea.insert(END, "=" * 60 + "\n")
    txtarea.insert(END, " THONG TIN BENH NHAN\n")
    txtarea.insert(END, "=" * 60 + "\n")
    txtarea.insert(END, f"  Ho ten: {namevalue.get()} | Tuoi: {agevalue.get()}\n")
    txtarea.insert(END, f"  Chuyen khoa: {symptomvalue.get().upper()}\n")
    txtarea.insert(END, f"  Vi tri: {locationvalue.get()}\n")
    txtarea.insert(END, "-" * 60 + "\n\n")

def update_ui_after_filter(val, success=True, error_msg=""):
    """Cập nhật UI sau khi filter xong"""
    global is_processing
    is_processing = False
    
    if success:
        user_entry_print()
        txtarea.insert(END, f">>> HE THONG DA CAP NHAT: {val.upper()}\n")
        txtarea.insert(END, "    (Danh sach benh vien da duoc thay doi)\n")
    else:
        messagebox.showerror("Loi Du Lieu", f"Khong the tai chuyen khoa!\n{error_msg}")

def auto_filter_hospitals(event):
    """Xử lý thay đổi chuyên khoa"""
    global is_processing
    
    val = symptomvalue.get()
    if not val or is_processing: 
        return
    
    is_processing = True
    
    def task():
        try:
            reset_graph()
            time.sleep(0.05)
            generate_hospital_dict(val)
            root.after(0, lambda: update_ui_after_filter(val, success=True))
        except Exception as e:
            error_msg = str(e)
            root.after(0, lambda: update_ui_after_filter(val, success=False, error_msg=error_msg))
    
    threading.Thread(target=task, daemon=True).start()

def filter_location_by_district(event):
    """Lọc địa điểm theo quận"""
    selected_district = districtvalue.get()
    new_locations = DISTRICTS_DATA.get(selected_district, nodes_list)
    location_combo['values'] = sorted(new_locations)
    location_combo.set('') 

def location_func():
    """Tìm đường đi tối ưu"""
    global is_processing
    
    if is_processing:
        messagebox.showwarning("Dang xu ly", "Vui long doi tac vu truoc hoan thanh!")
        return
    
    root.update_idletasks()
    l_1 = locationvalue.get()
    
    if not l_1:
        messagebox.showwarning("Canh bao", "Vui long chon Vi tri cu the!")
        return

    is_processing = True
    user_entry_print()
    txtarea.insert(END, "Dang tinh toan duong di toi uu...\n")
    root.update()

    try:
        loc_user = get_user_location(l_1)
        if loc_user is None:
            messagebox.showerror("Loi", "Dia diem chua co toa do!")
            is_processing = False
            return

        closest = find_closest_hospital(loc_user)
        if closest is None:
            txtarea.insert(END, "KHONG TIM THAY BENH VIEN PHU HOP!\n")
            is_processing = False
            return
             
        c_h_name, c_h_distance = closest[0], closest[1]

        create_user_edge(loc_user)

        dijkstra(G, 'Loc User')
        shortest_path = get_shortest_path('Loc User', c_h_name)

        full_message = ""
        if not shortest_path or len(shortest_path) == 0:
            full_message = f"BENH VIEN GAN NHAT: {c_h_name}\nKHOANG CACH TRUC TUYEN: {c_h_distance:.2f} km\n\n"
            full_message += "Luu y: Khong tim thay duong di tren ban do.\n"
            full_message += "Ban co the di chuyen truc tiep toi dia diem nay."
        else:
            path_names = [edge[1] for edge in shortest_path]
            path_str = " [Vi tri cua ban]\n     |\n     v\n"
            for i, node in enumerate(path_names):
                path_str += f"  {i+1}. {node}\n"
                if i < len(path_names) - 1:
                    path_str += "     |\n     v\n"            
            full_message = f"BENH VIEN TOI UU NHAT: {c_h_name}\nKHOANG CACH: {c_h_distance:.2f} km\n\nLO TRINH DI CHUYEN:\n\n{path_str}"
        
        info = give_hospital_info(c_h_name)
        txtarea.insert(END, "KET QUA TIM KIEM:\n")
        txtarea.insert(END, full_message)
        txtarea.insert(END, "\n" + "-"*35 + "\nTHONG TIN LIEN HE:" + info)
        txtarea.insert(END, "\n" + "="*60 + "\n")
        
    except Exception as e:
        messagebox.showerror("Loi Thuat Toan", f"Chi tiet: {e}")
    finally:
        is_processing = False

def emergency_func():
    """Gọi xe cấp cứu"""
    global is_processing
    
    if is_processing:
        messagebox.showwarning("Dang xu ly", "Vui long doi!")
        return
    
    is_processing = True
    txtarea.delete('1.0', END)
    txtarea.insert(END, "!!! KHAN CAP - TIM BENH VIEN GAN NHAT !!!\n")
    
    try:
        reset_graph()
        generate_hospital_dict('Da khoa') 
        
        l_1 = locationvalue.get()
        if not l_1: 
            l_1 = 'Cau Rong'
        
        loc_user = get_user_location(l_1)
        closest = find_closest_hospital(loc_user)
        
        if closest:
            name = closest[0]
            dist = closest[1]
            messagebox.showwarning("KHAN CAP", f"XE CAP CUU TU {name.upper()} DANG TOI!\nCach: {dist:.2f} km")
            txtarea.insert(END, f"\nDA DIEU XE TU: {name}\nKHOANG CACH: {dist:.2f} km\nSO DIEN THOAI: 115")
        else:
            messagebox.showerror("Loi", "Khong tim thay benh vien gan!")
            
    except Exception as e:
        messagebox.showerror("Loi", f"Khong the xu ly: {e}")
    finally:
        is_processing = False

def on_benchmark_finish(csv_file):
    """Callback khi benchmark xong"""
    global is_processing
    
    toggle_gui_state('normal')
    btn_benchmark.config(text="CHAY THUC NGHIEM")
    progress_bar.pack_forget()
    is_processing = False
    
    try:
        reset_graph()
        generate_hospital_dict('Da khoa')
        symptomvalue.set('Da khoa')
    except: 
        pass

    if csv_file:
        messagebox.showinfo("Thanh cong", f"Da thu thap du lieu xong!\nFile: {csv_file}")
        txtarea.insert(END, "\n" + "="*40 + "\n")
        txtarea.insert(END, ">>> KET QUA THUC NGHIEM:\n")
        txtarea.insert(END, f"-> Du lieu da luu tai: {csv_file}\n")
        txtarea.insert(END, "-> Hay nhan nut 'VE BIEU DO' de xem bao cao.\n")
    else:
        messagebox.showerror("Loi", "Khong tao duoc file du lieu.")

def thread_task_benchmark():
    """Luồng chạy benchmark"""
    try:
        for p in range(0, 90, 15):
            root.after(0, lambda val=p: progress_var.set(val))
            time.sleep(0.2)
        
        csv_file = benchmark_engine.run_benchmark_suite()
        
        root.after(0, lambda: progress_var.set(100))
        time.sleep(0.3)
        
        root.after(0, on_benchmark_finish, csv_file)
        
    except Exception as e:
        print(f"Benchmark Error: {e}")
        root.after(0, lambda: messagebox.showerror("Loi Benchmark", str(e)))
        root.after(0, lambda: toggle_gui_state('normal'))
        root.after(0, lambda: (btn_benchmark.config(text="CHAY THUC NGHIEM"), progress_bar.pack_forget()))

def run_benchmark_gui():
    """Nút chạy benchmark"""
    global is_processing
    
    if is_processing:
        messagebox.showwarning("Dang xu ly", "Vui long doi tac vu hien tai!")
        return
    
    is_processing = True
    txtarea.insert(END, "\n" + "="*40 + "\n")
    txtarea.insert(END, ">>> DANG CHAY DANH GIA (PLEASE WAIT)...\n")
    txtarea.insert(END, "He thong se tam khoa trong vai giay de xu ly...\n")
    
    toggle_gui_state('disabled')
    btn_benchmark.config(text="Dang xu ly...")
    
    progress_var.set(0)
    progress_bar.pack(fill=X, padx=10, pady=5)
    
    t = threading.Thread(target=thread_task_benchmark, daemon=True)
    t.start()

def run_visualizer_gui():
    """Vẽ biểu đồ"""
    try:
        if not os.path.exists("system_evaluation_data.csv"):
            messagebox.showwarning("Canh bao", "Chua co du lieu!\nVui long chay 'THUC NGHIEM' truoc.")
            return
        
        visualizer.draw_all_charts("system_evaluation_data.csv")
        messagebox.showinfo("Thanh cong", "Da xuat 3 bieu do anh vao thu muc du an.")
        
        if os.name == 'nt' and os.path.exists("Chart_3_Accuracy.png"):
            os.system("start Chart_3_Accuracy.png")
            
    except Exception as e:
        messagebox.showerror("Loi Ve Bieu Do", f"Chi tiet: {e}")

title_frame = Frame(root, bg='#2980B9', height=80)
title_frame.pack(fill=X)
Label(title_frame, text="HE THONG TIM KIEM BENH VIEN DA NANG", 
      font="Arial 22 bold", fg='white', bg='#2980B9', pady=15).pack()

main_frame = Frame(root, bg='#E8F4F8')
main_frame.pack(pady=10, padx=20, fill=BOTH, expand=True)

left_frame = Frame(main_frame, bg='white', relief=GROOVE, bd=2, width=450)
left_frame.pack(side=LEFT, padx=10, pady=10, fill=BOTH)
left_frame.pack_propagate(False) 

def create_field(parent, lbl, var, type='entry', vals=None, bind_func=None):
    f = Frame(parent, bg='white')
    f.pack(pady=5, padx=15, fill=X)
    Label(f, text=lbl, font="Arial 10 bold", bg='white', fg='#555', 
          width=15, anchor='w').pack(side=LEFT)
    
    if type=='entry': 
        widget = Entry(f, textvariable=var, width=22, bd=1, 
                      relief=SOLID, font="Arial 10")
        widget.pack(side=LEFT, ipady=3)
    else: 
        widget = ttk.Combobox(f, textvariable=var, values=vals, 
                             width=20, state='readonly', font="Arial 10")
        widget.pack(side=LEFT, ipady=3)
        if bind_func: 
            widget.bind("<<ComboboxSelected>>", bind_func) 
        if vals: 
            widget.current(0)
    return widget

Label(left_frame, text="NHAP THONG TIN", font="Arial 13 bold", 
      bg='white', fg='#2C3E50', pady=15).pack()

name_entry = create_field(left_frame, "Ho ten:", namevalue)
age_entry = create_field(left_frame, "Tuoi:", agevalue)
gender_combo = create_field(left_frame, "Gioi tinh:", gendervalue, 
                            'combo', ['Nam', 'Nu'])

Frame(left_frame, bg='#EEE', height=2).pack(fill=X, padx=15, pady=15)

Label(left_frame, text="BO LOC TIM KIEM", font="Arial 13 bold", 
      bg='white', fg='#2C3E50').pack(pady=5)

symptom_combo = create_field(left_frame, "Chuyen khoa:", symptomvalue, 
                             'combo', symptom_list, auto_filter_hospitals)

district_list = list(DISTRICTS_DATA.keys())
district_combo = create_field(left_frame, "Chon Khu vuc:", districtvalue, 
                              'combo', district_list, filter_location_by_district)

f_loc = Frame(left_frame, bg='white')
f_loc.pack(pady=5, padx=15, fill=X)
Label(f_loc, text="Vi tri cua ban:", font="Arial 10 bold", 
      bg='white', fg='#555', width=15, anchor='w').pack(side=LEFT)
location_combo = ttk.Combobox(f_loc, textvariable=locationvalue, 
                             values=sorted(nodes_list), width=20, 
                             state='readonly', font="Arial 10")
location_combo.pack(side=LEFT, ipady=3)

btn_frame = Frame(left_frame, bg='white')
btn_frame.pack(pady=15)

btn_find = Button(btn_frame, text="TIM DUONG DI", command=location_func, 
                 bg='#27AE60', fg='white', font='Arial 11 bold', 
                 width=18, height=2, cursor='hand2')
btn_find.pack(pady=5)

btn_emergency = Button(btn_frame, text="GOI KHAN CAP", command=emergency_func, 
                      bg='#C0392B', fg='white', font='Arial 11 bold', 
                      width=18, cursor='hand2')
btn_emergency.pack(pady=5)

Frame(left_frame, bg='#EEE', height=2).pack(fill=X, padx=15, pady=10)

Label(left_frame, text="DANH GIA HE THONG", font="Arial 12 bold", 
      bg='white', fg='#8E44AD').pack(pady=2)

eval_frame = Frame(left_frame, bg='white')
eval_frame.pack(pady=5)

btn_benchmark = Button(eval_frame, text="CHAY THUC NGHIEM", 
                      command=run_benchmark_gui, bg='#8E44AD', 
                      fg='white', font='Arial 10 bold', width=20, cursor='hand2')
btn_benchmark.pack(pady=3)

btn_visualize = Button(eval_frame, text="VE BIEU DO BAO CAO", 
                      command=run_visualizer_gui, bg='#9B59B6', 
                      fg='white', font='Arial 10 bold', width=20, cursor='hand2')
btn_visualize.pack(pady=3)

right_frame = Frame(main_frame, bg='white', relief=GROOVE, bd=2)
right_frame.pack(side=RIGHT, padx=10, pady=10, fill=BOTH, expand=True)

Label(right_frame, text="KET QUA & CHI DAN", font="Arial 12 bold", 
      bg='#34495E', fg='white', pady=8).pack(fill=X)

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(right_frame, variable=progress_var, maximum=100)

scroll = Scrollbar(right_frame)
txtarea = Text(right_frame, yscrollcommand=scroll.set, 
              font=('Consolas', 11), bg='#F9F9F9', 
              padx=15, pady=15, wrap=WORD)
scroll.config(command=txtarea.yview)
scroll.pack(side=RIGHT, fill=Y)
txtarea.pack(fill=BOTH, expand=1)

try:
    reset_graph()
    generate_hospital_dict('Da khoa')
    symptomvalue.set('Da khoa')
    districtvalue.set('Tat ca')
except Exception as e:
    print(f"Initialization error: {e}")

root.mainloop()