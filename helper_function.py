import geocoder
import geopy
import numpy as np
import geopy.distance
from geopy.geocoders import Nominatim

def choose1():
    """Get user location from IP (not used in current implementation)"""
    ip = geocoder.ip('me')
    user_loc = ip.latlng
    user_loc = (user_loc[1], user_loc[0])
    return user_loc

def distance(loc1, loc2):
    """Calculate distance between 2 coordinates"""
    ans = geopy.distance.geodesic(loc1, loc2).km
    return ans

def nearest_node(userloc, G):
    """
    Find the closest node from a location
    Args:
        userloc: tuple (lat, lng)
        G: dict {node_name: (lat, lng)}
    Returns:
        tuple (node_name, distance_km)
    """
    if not G or not userloc:
        return None
    
    em = []
    for node_name in G:
        coords_1 = (userloc[0], userloc[1]) 
        value = G[node_name]
 
        if isinstance(value, (list, tuple)) and len(value) >= 2:
            lat_h, lng_h = value[0], value[1]
        else:
            continue
            
        coords_2 = (lat_h, lng_h)  
        dist = geopy.distance.geodesic(coords_2, coords_1).km
        em.append([node_name, dist])
    
    if not em:
        return None

    least = ''
    value = 999999999999
    for item in em: 
        if item[1] < value:
            least = item[0]
            value = item[1]
    
    return least, value

def enQueue(lst, a):
    """Add element to queue"""
    lst.append(a)
    return lst

def deQueue(lst):
    """Remove first element from queue"""
    a = lst.pop(0)
    return a

def dijkstra(graph, source):
    """
    Dijkstra's shortest path algorithm
    Args:
        graph: dict {node: [(neighbor, weight), ...]}
        source: starting node name
    Returns:
        dict {node: [previous_node, distance]}
    """
    if source not in graph:
        print(f"Warning: Source node '{source}' not in graph")
        return {source: [source, 0]}
    
    dj = {}  
    dj[source] = [source, 0]

    for node in graph:
        if node != source:
            dj[node] = ['-', 999999999]
    
    visited = []
    
    while len(dj) != len(visited):

        min_dist = 999999999
        min_node = None
        
        for node in dj:
            if node not in visited and dj[node][1] < min_dist:
                min_node = node
                min_dist = dj[node][1]
        
        if min_node is None:
            break  
        
        visited.append(min_node)

        if min_node in graph:
            for neighbor_info in graph[min_node]:
                neighbor = neighbor_info[0]
                weight = neighbor_info[1]
                distance = dj[min_node][1] + weight
                
                if neighbor in dj and dj[neighbor][1] > distance:
                    dj[neighbor][1] = distance
                    dj[neighbor][0] = min_node
    
    return dj

def getShortestPath(graph, source, target):
    """
    ✅ FIXED VERSION - Get shortest path between source and target
    Args:
        graph: dict {node: [(neighbor, weight), ...]}
        source: starting node
        target: destination node
    Returns:
        list of tuples [(from_node, to_node), ...]
    """

    dist = dijkstra(graph, source)
 
    if target not in dist or dist[target][1] == 999999999:
        print(f"No path from {source} to {target}")
        return []

    path = []
    current = target

    while current != source:
        previous = dist[current][0]
        
        if previous == '-':
            print(f"Path broken at {current}")
            return []
        
        path.append((previous, current))
        current = previous

    path.reverse()
    
    distance_shortest = dist[target][1]
    print(f'The nearest hospital is {distance_shortest:.2f} km away.')
    
    return path

def heuristic(node1, node2, coords_dict):
    """Calculate straight-line distance heuristic"""
    if node1 not in coords_dict or node2 not in coords_dict:
        return 0
    return distance(coords_dict[node1], coords_dict[node2])

def astar_search(graph, start, goal, coords_dict):
    """
    A* pathfinding algorithm (faster than Dijkstra for single target)
    Not used in current implementation but provided as alternative
    """
    from heapq import heappush, heappop
    
    open_set = []
    heappush(open_set, (0, start))
    
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal, coords_dict)}
    
    while open_set:
        current = heappop(open_set)[1]
        
        if current == goal:
            path = []
            while current in came_from:
                prev = came_from[current]
                path.append((prev, current))
                current = prev
            return path[::-1]
        
        if current not in graph:
            continue
        
        for neighbor, weight in graph[current]:
            tentative_g = g_score.get(current, 999999999) + weight
            
            if tentative_g < g_score.get(neighbor, 999999999):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor, goal, coords_dict)
                heappush(open_set, (f_score[neighbor], neighbor))
    
    return []  