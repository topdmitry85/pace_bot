import gpxpy
import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def min_per_km(seconds_per_meter):
    if seconds_per_meter == 0:
        return float('inf')
    pace = 1000 / seconds_per_meter  # meters per second
    minutes = int(60 / pace)
    seconds = int((60 / pace - minutes) * 60)
    return f"{minutes}:{seconds:02d}"

def parse_gpx(gpx_file_path):
    with open(gpx_file_path, 'r') as f:
        gpx = gpxpy.parse(f)

    segments = []
    for track in gpx.tracks:
        for segment in track.segments:
            points = segment.points
            if len(points) < 2:
                continue
            i = 0
            while i < len(points) - 1:
    start = points[i]
    dist = 0
    j = i + 1
    while j < len(points):
        d = haversine(start.latitude, start.longitude,
                      points[j].latitude, points[j].longitude)
        dist += d
        if dist >= 20:  # изменили 10 -> 20 метров
            break
        j += 1
    if j >= len(points):
        break
    duration = (points[j].time - start.time).total_seconds()

    # 🔍 фильтр слишком коротких сегментов
    if duration <= 3 or dist <= 0:
        i = j
        continue

    segments.append({
        'distance': dist,
        'duration': duration,
        'start_km': sum(s['distance'] for s in segments) / 1000
    })
    i = j
    
    return segments

def process_gpx_file(file_path):
    segments = parse_gpx(file_path)

    # Фильтруем некорректные сегменты
    segments = [s for s in segments if s['distance'] > 0 and s['duration'] > 0]

    if not segments:
        return "❌ Недостаточно корректных данных для анализа GPX-файла."

    # Расчёт темпов
    paces = [seg['duration'] / seg['distance'] for seg in segments]
    avg_pace = sum(paces) / len(paces)
    stddev = math.sqrt(sum((p - avg_pace)**2 for p in paces) / len(paces))

    # Индексы самого стабильного и нестабильного сегментов
    closest_idx = min(range(len(paces)), key=lambda i: abs(paces[i] - avg_pace))
    worst_idx = max(range(len(paces)), key=lambda i: abs(paces[i] - avg_pace))

    # Разница в темпе с форматированием
    def pace_diff(p):
        delta_sec = int(p * 1000)
        minutes = delta_sec // 60
        seconds = delta_sec % 60
        sign = "+" if p >= 0 else "-"
        return f"{sign}{abs(minutes)}:{abs(seconds):02d}"

    result = (
        "🏁 GPX-анализ завершён:\n\n"
        f"— Средний темп: {min_per_km(avg_pace)} /км\n"
        f"— СКО темпа: {pace_diff(stddev)} /км\n\n"
        f"🎯 Самый стабильный отрезок:\n"
        f"— Отметка {segments[closest_idx]['start_km']:.2f} км\n"
        f"— Темп: {min_per_km(paces[closest_idx])} /км\n"
        f"— Отклонение: {pace_diff(paces[closest_idx] - avg_pace)}\n\n"
        f"⚠️ Самый нестабильный отрезок:\n"
        f"— Отметка {segments[worst_idx]['start_km']:.2f} км\n"
        f"— Темп: {min_per_km(paces[worst_idx])} /км\n"
        f"— Отклонение: {pace_diff(paces[worst_idx] - avg_pace)}"
    )
    return result

