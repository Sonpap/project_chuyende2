import geocoder
import geopy
import numpy as np
import geopy.distance
from geopy.geocoders import Nominatim
from helper_function import *
import threading
import copy

nodes_coord = {
    # Khu vực Hải Châu và Trung Tâm
    'San Bay Da Nang': (16.0439, 108.1994),
    'Ga Da Nang': (16.0700, 108.2130),
    'Cau Rong': (16.0611, 108.2257),
    'Cho Han': (16.0689, 108.2246),
    'Cho Con': (16.0681, 108.2137),
    'Trung tam Hanh chinh': (16.0776, 108.2230),
    'Bao tang Cham': (16.0607, 108.2234),
    'Cong vien APEC': (16.0600, 108.2230),
    'Nha hat Trung Vuong': (16.0690, 108.2210),
    'San van dong Chi Lang': (16.0650, 108.2180),
    'Dai hoc Duy Tan': (16.0601, 108.2104),
    'Khach san Novotel': (16.0780, 108.2235),
    'Khach san Hilton': (16.0750, 108.2240),

    # Khu vực Thanh Khê
    'Cong vien 29/3': (16.0555, 108.2005),
    'Sieu thi Co.op Mart': (16.0550, 108.1950),
    'Nga Ba Hue': (16.0583, 108.1819),
    'Tuong dai Me Nhu': (16.0550, 108.1750),
    'Dai hoc The Duc The Thao': (16.0500, 108.1800),

    # Khu vực Sơn Trà và biển
    'Cau Song Han': (16.0722, 108.2266),
    'Vincom Ngo Quyen': (16.0735, 108.2312),
    'Cau Tinh Yeu': (16.0615, 108.2280),
    'Bien My Khe': (16.0600, 108.2435),
    'Cong vien Bien Dong': (16.0650, 108.2450),
    'Cau Thuan Phuoc': (16.0940, 108.2230),
    'Chua Linh Ung (Son Tra)': (16.1070, 108.2750),
    'InterContinental Resort': (16.1200, 108.3000),
    'Khach san Muong Thanh': (16.0580, 108.2450),

    # Khu vực Ngũ Hành Sơn
    'Ngu Hanh Son (Danh thang)': (16.0029, 108.2638),
    'Dai hoc Kinh Te': (16.0350, 108.2350),
    'FPT City': (15.9800, 108.2600),
    'Resort Furama': (16.0300, 108.2450),
    'Lotte Mart': (16.0350, 108.2300),
    'Cong vien Chau A (Asia Park)': (16.0396, 108.2263),
    'Helio Center': (16.0357, 108.2242),

    # Khu vực Liên Chiểu
    'Ben xe Trung Tam': (16.0480, 108.1700),
    'Dai hoc Bach Khoa': (16.0754, 108.1536),
    'Dai hoc Su Pham': (16.0650, 108.1600),
    'Khu Cong Nghiep Hoa Khanh': (16.0700, 108.1400),
    'Bai tam Xuan Thieu': (16.0800, 108.1600),

    # Khu vực Cẩm Lệ
    'Trung tam Hoi cho Trien lam': (16.0200, 108.2150),
    'Cau Rong (Duoi cau phia Dong)': (16.0610, 108.2260),

    # Danh sách bệnh viện
    'Benh vien Da Nang': (16.0678, 108.2170),           
    'Benh vien Hoan My': (16.0605, 108.2075),           
    'Benh vien Gia Dinh': (16.0640, 108.2150),          
    'Benh vien C Da Nang': (16.0695, 108.2188),                 
    'Benh vien Vinmec': (16.0535, 108.2280),            
    'Benh vien Mat Da Nang': (16.0715, 108.2185),               
    'Benh vien Da Lieu': (16.0632, 108.2125),           
    'Benh vien Phu San - Nhi': (16.0270, 108.2390),     
    'Benh vien Ung Buou': (16.0590, 108.1750),          
    'Benh vien Rang Ham Mat': (16.0655, 108.2195),
    'Benh vien Chinh hinh va PHCN': (16.0690, 108.2160), 
    'Benh vien Tam Than Da Nang': (16.0650, 108.1550),
    'Trung tam Noi tiet Da Nang': (16.0650, 108.2180),
    'Benh vien 199 Bo Cong An': (16.0750, 108.2400),
    'Benh vien Tam Tri': (16.0468, 108.2112),            
    'Benh vien Y Hoc Co Truyen': (16.0300, 108.2150),
    'Benh vien Phoi Da Nang': (16.0350, 108.2000),
    'Phong kham Pasteur': (16.0700, 108.2300),
    'Phong kham Thien Nhan': (16.0560, 108.2020),
    'Benh vien Giao Thong Van Tai': (16.0620, 108.1650),
    'Benh vien Binh Dan': (16.0598, 108.2055)
}

nodes_list = sorted([k for k in nodes_coord.keys() 
                     if 'Benh vien' not in k 
                     and 'Trung tam Noi tiet' not in k 
                     and 'Phong kham' not in k])

hospital_info = {
    'Benh vien Da Nang':            [nodes_coord['Benh vien Da Nang'], 4.5, '0236 3821 118', 'general'], 
    'Benh vien Hoan My':            [nodes_coord['Benh vien Hoan My'], 4.7, '0236 3650 676', 'cardiology'], 
    'Benh vien Gia Dinh':           [nodes_coord['Benh vien Gia Dinh'], 4.6, '1900 2250', 'gastroenterology'], 
    'Benh vien C Da Nang':          [nodes_coord['Benh vien C Da Nang'], 4.2, '0236 3821 480', 'endocrinology'], 
    'Benh vien Vinmec':             [nodes_coord['Benh vien Vinmec'], 4.9, '0236 3711 111', 'general'], 
    'Benh vien Mat Da Nang':        [nodes_coord['Benh vien Mat Da Nang'], 4.4, '0236 3644 555', 'ophthalmology'],
    'Benh vien Da Lieu':            [nodes_coord['Benh vien Da Lieu'], 4.3, '0236 3756 182', 'dermatology'],
    'Benh vien Phu San - Nhi':      [nodes_coord['Benh vien Phu San - Nhi'], 4.8, '0236 3957 777', 'obstetrics'],
    'Benh vien Ung Buou':           [nodes_coord['Benh vien Ung Buou'], 4.5, '0236 3717 717', 'oncology'],
    'Benh vien Rang Ham Mat':       [nodes_coord['Benh vien Rang Ham Mat'], 4.1, '0236 3826 360', 'dental'],
    'Benh vien Chinh hinh va PHCN': [nodes_coord['Benh vien Chinh hinh va PHCN'], 4.3, '0236 3822 222', 'orthopedics'],
    'Benh vien Tam Than Da Nang':   [nodes_coord['Benh vien Tam Than Da Nang'], 4.0, '0236 3123 456', 'neurology'], 
    'Trung tam Noi tiet Da Nang':   [nodes_coord['Trung tam Noi tiet Da Nang'], 4.2, '0236 3777 888', 'endocrinology'],
    'Benh vien 199 Bo Cong An':     [nodes_coord['Benh vien 199 Bo Cong An'], 4.4, '1900 986868', 'orthopedics'], 
    'Benh vien Tam Tri':            [nodes_coord['Benh vien Tam Tri'], 4.1, '0236 3679 555', 'neurology'], 
    'Benh vien Y Hoc Co Truyen':    [nodes_coord['Benh vien Y Hoc Co Truyen'], 4.1, '0236 3678 999', 'general'],
    'Benh vien Phoi Da Nang':       [nodes_coord['Benh vien Phoi Da Nang'], 4.0, '0236 3456 789', 'general'],
    'Phong kham Pasteur':           [nodes_coord['Phong kham Pasteur'], 4.5, '0236 3888 777', 'gastroenterology'], 
    'Phong kham Thien Nhan':        [nodes_coord['Phong kham Thien Nhan'], 4.6, '0236 3555 666', 'general'], 
    'Benh vien Giao Thong Van Tai': [nodes_coord['Benh vien Giao Thong Van Tai'], 3.9, '0236 3222 333', 'general'],
    'Benh vien Binh Dan':           [nodes_coord['Benh vien Binh Dan'], 4.0, '0236 3714 030', 'endocrinology'] 
}

BASE_GRAPH = {
    'Trung tam Hanh chinh': [('Benh vien Da Nang', 0.8), ('Khach san Novotel', 0.2), ('Cau Song Han', 1.0)],
    'Khach san Novotel': [('Trung tam Hanh chinh', 0.2), ('Khach san Hilton', 0.5)],
    'Khach san Hilton': [('Khach san Novotel', 0.5), ('Cho Han', 0.8)],
    'Cho Han': [('Khach san Hilton', 0.8), ('Cau Song Han', 0.5), ('Benh vien C Da Nang', 0.6)],
    'Cau Song Han': [('Cho Han', 0.5), ('Vincom Ngo Quyen', 1.2)],
    'Benh vien Da Nang': [('Trung tam Hanh chinh', 0.8), ('Benh vien C Da Nang', 0.4), ('San van dong Chi Lang', 0.5)],
    'San van dong Chi Lang': [('Benh vien Da Nang', 0.5), ('Benh vien Gia Dinh', 0.8)],
    'Benh vien C Da Nang': [('Benh vien Da Nang', 0.4), ('Cho Han', 0.6), ('Benh vien Chinh hinh va PHCN', 0.3)],
    'Benh vien Chinh hinh va PHCN': [('Benh vien C Da Nang', 0.3), ('Trung tam Noi tiet Da Nang', 0.5)],
    'Trung tam Noi tiet Da Nang': [('Benh vien Chinh hinh va PHCN', 0.5), ('Benh vien Rang Ham Mat', 0.3)],
    'Benh vien Rang Ham Mat': [('Trung tam Noi tiet Da Nang', 0.3), ('Nha hat Trung Vuong', 0.4)],
    'Nha hat Trung Vuong': [('Benh vien Rang Ham Mat', 0.4), ('Cho Con', 0.8)],
    'Cho Con': [('Nha hat Trung Vuong', 0.8), ('Benh vien Gia Dinh', 0.6)],
    'Benh vien Gia Dinh': [('Cho Con', 0.6), ('Benh vien Da Lieu', 0.4), ('San van dong Chi Lang', 0.8)],
    'Benh vien Da Lieu': [('Benh vien Gia Dinh', 0.4), ('Dai hoc Duy Tan', 0.3)],
    'Dai hoc Duy Tan': [('Benh vien Da Lieu', 0.3), ('Cau Rong', 1.5)],
    'Cau Rong': [('Bao tang Cham', 0.3), ('Cong vien APEC', 0.4), ('Cau Tinh Yeu', 0.8)],
    'Bao tang Cham': [('Cau Rong', 0.3), ('Benh vien Hoan My', 1.2)],
    'Cong vien APEC': [('Cau Rong', 0.4), ('Benh vien Hoan My', 1.5)],
    'Benh vien Hoan My': [('Bao tang Cham', 1.2), ('Cong vien APEC', 1.5), ('San Bay Da Nang', 1.5), ('Benh vien Binh Dan', 0.5)],
    'Benh vien Binh Dan': [('Benh vien Hoan My', 0.5), ('Phong kham Thien Nhan', 0.5)],
    'Phong kham Thien Nhan': [('Benh vien Binh Dan', 0.5), ('Cong vien 29/3', 0.6)],
    'Cong vien 29/3': [('Phong kham Thien Nhan', 0.6), ('Sieu thi Co.op Mart', 0.5)],
    'Sieu thi Co.op Mart': [('Cong vien 29/3', 0.5), ('Nga Ba Hue', 1.2)],
    'San Bay Da Nang': [('Benh vien Hoan My', 1.5), ('Nga Ba Hue', 2.0)],
    'Nga Ba Hue': [('Sieu thi Co.op Mart', 1.2), ('San Bay Da Nang', 2.0), ('Tuong dai Me Nhu', 1.0)],
    'Tuong dai Me Nhu': [('Nga Ba Hue', 1.0), ('Dai hoc The Duc The Thao', 0.8)],
    'Dai hoc The Duc The Thao': [('Tuong dai Me Nhu', 0.8), ('Benh vien Giao Thong Van Tai', 1.5)],
    'Benh vien Giao Thong Van Tai': [('Dai hoc The Duc The Thao', 1.5), ('Benh vien Ung Buou', 1.0)],
    'Benh vien Ung Buou': [('Benh vien Giao Thong Van Tai', 1.0), ('Benh vien Tam Than Da Nang', 0.8)],
    'Benh vien Tam Than Da Nang': [('Benh vien Ung Buou', 0.8), ('Dai hoc Su Pham', 1.2)],
    'Dai hoc Su Pham': [('Benh vien Tam Than Da Nang', 1.2), ('Dai hoc Bach Khoa', 0.8)],
    'Dai hoc Bach Khoa': [('Dai hoc Su Pham', 0.8), ('Khu Cong Nghiep Hoa Khanh', 1.5)],
    'Khu Cong Nghiep Hoa Khanh': [('Dai hoc Bach Khoa', 1.5), ('Bai tam Xuan Thieu', 2.0)],
    'Bai tam Xuan Thieu': [('Khu Cong Nghiep Hoa Khanh', 2.0), ('Ben xe Trung Tam', 3.0)],
    'Ben xe Trung Tam': [('Bai tam Xuan Thieu', 3.0), ('Nga Ba Hue', 2.5)],
    'Vincom Ngo Quyen': [('Cau Song Han', 1.2), ('Cau Tinh Yeu', 1.0), ('Benh vien 199 Bo Cong An', 1.5)],
    'Cau Tinh Yeu': [('Cau Rong', 0.8), ('Vincom Ngo Quyen', 1.0), ('Cau Rong (Duoi cau phia Dong)', 0.5)],
    'Cau Rong (Duoi cau phia Dong)': [('Cau Tinh Yeu', 0.5), ('Benh vien Vinmec', 2.0), ('Bien My Khe', 1.5)],
    'Benh vien 199 Bo Cong An': [('Vincom Ngo Quyen', 1.5), ('Phong kham Pasteur', 0.5), ('Cong vien Bien Dong', 1.5)],
    'Phong kham Pasteur': [('Benh vien 199 Bo Cong An', 0.5), ('Bien My Khe', 1.0)],
    'Cong vien Bien Dong': [('Benh vien 199 Bo Cong An', 1.5), ('Bien My Khe', 1.0)],
    'Bien My Khe': [('Cong vien Bien Dong', 1.0), ('Phong kham Pasteur', 1.0), ('Cau Rong (Duoi cau phia Dong)', 1.5), ('Khach san Muong Thanh', 1.0)],
    'Khach san Muong Thanh': [('Bien My Khe', 1.0), ('Resort Furama', 2.0)],
    'Cau Thuan Phuoc': [('Vincom Ngo Quyen', 3.0), ('InterContinental Resort', 5.0)],
    'Chua Linh Ung (Son Tra)': [('InterContinental Resort', 2.0)],
    'InterContinental Resort': [('Chua Linh Ung (Son Tra)', 2.0), ('Cau Thuan Phuoc', 5.0)],
    'Benh vien Vinmec': [('Cau Rong (Duoi cau phia Dong)', 2.0), ('Benh vien Tam Tri', 1.0), ('Lotte Mart', 1.5)],
    'Benh vien Tam Tri': [('Benh vien Vinmec', 1.0), ('Helio Center', 1.2)],
    'Helio Center': [('Benh vien Tam Tri', 1.2), ('Cong vien Chau A (Asia Park)', 0.5)],
    'Cong vien Chau A (Asia Park)': [('Helio Center', 0.5), ('Lotte Mart', 0.8)],
    'Lotte Mart': [('Cong vien Chau A (Asia Park)', 0.8), ('Benh vien Vinmec', 1.5), ('Dai hoc Kinh Te', 1.0)],
    'Dai hoc Kinh Te': [('Lotte Mart', 1.0), ('Benh vien Phu San - Nhi', 1.5)],
    'Benh vien Phu San - Nhi': [('Dai hoc Kinh Te', 1.5), ('Resort Furama', 1.0), ('Ngu Hanh Son (Danh thang)', 2.0)],
    'Resort Furama': [('Benh vien Phu San - Nhi', 1.0), ('Khach san Muong Thanh', 2.0)],
    'Ngu Hanh Son (Danh thang)': [('Benh vien Phu San - Nhi', 2.0), ('FPT City', 3.0)],
    'FPT City': [('Ngu Hanh Son (Danh thang)', 3.0)],
    'Trung tam Hoi cho Trien lam': [('Benh vien Y Hoc Co Truyen', 1.5)],
    'Benh vien Y Hoc Co Truyen': [('Trung tam Hoi cho Trien lam', 1.5), ('Benh vien Phoi Da Nang', 1.0)],
    'Benh vien Phoi Da Nang': [('Benh vien Y Hoc Co Truyen', 1.0), ('Benh vien Tam Tri', 2.0)],
    'Benh vien Mat Da Nang': [('Benh vien Da Nang', 0.5), ('Trung tam Hanh chinh', 0.8), ('Benh vien Rang Ham Mat', 0.3)],
    'Ga Da Nang': [('Benh vien Da Nang', 1.0), ('Cho Han', 0.8)]
}

_graph_lock = threading.Lock()
_hospital_coord_lock = threading.Lock()  
G = {}
hospital_coord = {}
hospital_list = []

def reset_graph():
    """Khôi phục graph về trạng thái ban đầu"""
    global G
    with _graph_lock:
        G.clear()
        for k, v in BASE_GRAPH.items():
            G[k] = list(v)  

def get_user_location(place):
    """Thread-safe location getter"""
    return nodes_coord.get(place)

def find_closest_hospital(loc_user):
    """Thread-safe hospital finder"""
    with _hospital_coord_lock:
        if not hospital_coord or not loc_user: 
            return None
        return nearest_node(loc_user, hospital_coord)

def generate_hospital_dict(specialty_vn):
    """✅ Thread-safe hospital filter"""
    global hospital_coord, hospital_list
    
    base_coord = {k: v for k, v in nodes_coord.items() if k in hospital_info}
    
    mapping = {
        'Tim mach': 'cardiology', 'Nha khoa': 'dental', 'Mat': 'ophthalmology',
        'Phu san': 'obstetrics', 'Chan thuong chinh hinh': 'orthopedics',
        'Than kinh': 'neurology', 'Noi tiet': 'endocrinology', 'Tieu hoa': 'gastroenterology',
        'Da lieu': 'dermatology', 'Ung buou': 'oncology', 'Da khoa': 'general'
    }
    
    target_dept = mapping.get(specialty_vn, 'general')
    filtered_coord = {}
    filtered_info = {}
    major_hospitals = ['Benh vien Da Nang', 'Benh vien Vinmec']
    
    for name, info in hospital_info.items():
        dept = info[3]
        if dept == target_dept or (target_dept == 'general' and dept == 'general'):
            filtered_coord[name] = base_coord[name]
            filtered_info[name] = info
    
    if not filtered_coord:
        for name in major_hospitals:
            filtered_coord[name] = base_coord[name]
            filtered_info[name] = hospital_info[name]
    
    with _hospital_coord_lock:
        hospital_coord = filtered_coord
        hospital_list = list(filtered_coord.keys())
    
    return filtered_info, filtered_coord

def create_user_edge(loc_user):
    """✅ Thread-safe edge creation"""
    global G
    
    closest_node = nearest_node(loc_user, nodes_coord)
    if not closest_node:
        raise ValueError("Cannot find nearest node")
    
    node_name = closest_node[0]
    dist = closest_node[1]
    
    with _graph_lock:
        if 'Loc User' in G:
            del G['Loc User']
        for node in list(G.keys()):
            if isinstance(G[node], list):
                G[node] = [(n, d) for n, d in G[node] if n != 'Loc User']
        G['Loc User'] = [(node_name, dist)]
        if node_name in G:
            existing = [n for n, d in G[node_name]]
            if 'Loc User' not in existing:
                G[node_name].append(('Loc User', dist))

def get_shortest_path(source, target):
    """✅ Thread-safe pathfinding"""
    with _graph_lock:
        try:
            if source not in G: 
                return []
            return getShortestPath(G, source, target)
        except Exception as e:
            print(f"Path error: {e}")
            return []

def give_hospital_info(name):
    """Lấy thông tin bệnh viện"""
    if name in hospital_info:
        i = hospital_info[name]
        mapping_reverse = {
            'general': 'Đa khoa', 'cardiology': 'Tim mạch', 'dental': 'Nha khoa',
            'ophthalmology': 'Mắt', 'obstetrics': 'Sản - Nhi', 'orthopedics': 'Chấn thương chỉnh hình',
            'neurology': 'Thần kinh', 'endocrinology': 'Nội tiết', 'gastroenterology': 'Tiêu hóa',
            'dermatology': 'Da liễu', 'oncology': 'Ung bướu'
        }
        dept_vn = mapping_reverse.get(i[3], i[3])
        return f"\n  Đánh giá: {i[1]}/5.0\n  Hotline: {i[2]}\n  Thế mạnh: {dept_vn}"
    return ""
try:
    reset_graph()
    generate_hospital_dict('Da khoa')
except Exception as e:
    print(f"Init error: {e}")