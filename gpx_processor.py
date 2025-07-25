import xml.etree.ElementTree as ET
from datetime import datetime
import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # м
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def parse_gpx(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    ns = {'default': 'http://www.topografix.com/GPX/1/1'}
    points = []

    for trkpt in root.findall('.//default:trkpt', ns):
        lat = float(trkpt.attrib['lat'])
        lon = float(trkpt.attrib['lon'])
        time_elem = trkpt.find('default:time', ns)
        if time_elem is not None:
            time = datetime.fromisoformat(time_elem.text.replace("Z", "+00:00"))
            points.append((lat, lon, time))

    return points

def format_pace(pace):
    if pace <= 0 or not math.isfinite(pace):
        return "—"
    total_seconds = int(round(pace * 1000))  # сек/км
    return f"{total_seconds // 60}:{total_seconds % 60:02d}"

def analyze_gpx(file_path):
    points = parse_gpx(file_path)
    if len(points) < 2:
        return "❌ Недостаточно точек для анализа."

    total_distance = 0
    start_time = points[0][2]
    end_time = points[-1][2]

    segments = []
    i = 0
    while i < len(points) - 1:
        seg_dist = 0
        j = i + 1
        while j < len(points):
            d = haversine(points[i][0], points[i][1], points[j][0], points[j][1])
            seg_dist += d
            if seg_dist >= 20:
                break
            j += 1
        if j >= len(points):
            break
        dt = (points[j][2] - points[i][2]).total_seconds()
        if dt <= 3 or seg_dist <= 0:
            i = j
            continue
        pace = dt / seg_dist  # сек/м
        segments.append({
            'distance': seg_dist,
            'duration': dt,
            'start_km': total_distance / 1000,
            'pace': pace
        })
        total_distance += seg_dist
        i = j

    duration = (end_time - start_time).total_seconds()
    avg_pace = duration / total_distance if total_distance > 0 else float('inf')
    paces = [s['pace'] for s in segments]
    stddev = math.sqrt(sum((p - avg_pace/1000)**2 for p in paces) / len(paces)) if paces else 0

    closest_idx = min(range(len(paces)), key=lambda i: abs(paces[i] - avg_pace / 1000))
    worst_idx = max(range(len(paces)), key=lambda i: abs(paces[i] - avg_pace / 1000))

    def pace_diff(p):
        if not math.isfinite(p):
            return "—"
        delta = (p - avg_pace / 1000) * 1000
        sign = "+" if delta >= 0 else "-"
        delta = abs(delta)
        return f"{sign}{int(delta // 60)}:{int(round(delta % 60)):02d}"

    result = (
        "🏁 GPX-анализ завершён:\n\n"
        f"— Дистанция: {total_distance / 1000:.2f} км\n"
        f"— Время: {int(duration // 60):02d}:{int(duration % 60):02d}\n"
        f"— Средний темп: {format_pace(avg_pace / 1000)} /км\n"
        f"— СКО темпа: {pace_diff(stddev)} /км\n\n"
        f"🎯 Самый стабильный отрезок:\n"
        f"— Отметка: {segments[closest_idx]['start_km']:.2f} км\n"
        f"— Темп: {format_pace(segments[closest_idx]['pace'])} /км\n"
        f"— Отклонение: {pace_diff(segments[closest_idx]['pace'])}\n\n"
        f"⚠️ Самый нестабильный отрезок:\n"
        f"— Отметка: {segments[worst_idx]['start_km']:.2f} км\n"
        f"— Темп: {format_pace(segments[worst_idx]['pace'])} /км\n"
        f"— Отклонение: {pace_diff(segments[worst_idx]['pace'])}"
    )
    return result
