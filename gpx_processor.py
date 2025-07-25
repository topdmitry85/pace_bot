import gpxpy
import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # радиус Земли в метрах
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def format_pace(seconds_per_km):
    if not math.isfinite(seconds_per_km) or seconds_per_km <= 0:
        return "—"
    minutes = int(seconds_per_km // 60)
    seconds = int(round(seconds_per_km % 60))
    return f"{minutes}:{seconds:02d}"

def pace_difference(delta_sec_per_km):
    if not math.isfinite(delta_sec_per_km):
        return "—"
    sign = "+" if delta_sec_per_km >= 0 else "-"
    delta_sec_per_km = abs(delta_sec_per_km)
    minutes = int(delta_sec_per_km // 60)
    seconds = int(round(delta_sec_per_km % 60))
    return f"{sign}{minutes}:{seconds:02d}"

def analyze_gpx(file_path):
    with open(file_path, 'r') as f:
        gpx = gpxpy.parse(f)

    all_points = []
    for track in gpx.tracks:
        for segment in track.segments:
            all_points.extend(segment.points)

    if len(all_points) < 2:
        return "❌ Недостаточно точек в файле."

    total_distance = 0
    start_time = all_points[0].time
    end_time = all_points[-1].time

    segment_list = []
    i = 0
    while i < len(all_points) - 1:
        dist = 0
        j = i + 1
        while j < len(all_points):
            d = haversine(all_points[i].latitude, all_points[i].longitude,
                          all_points[j].latitude, all_points[j].longitude)
            dist += d
            if dist >= 20:
                break
            j += 1
        if j >= len(all_points):
            break

        duration = (all_points[j].time - all_points[i].time).total_seconds()

        # Пропускаем слишком короткие или нулевые сегменты
        if duration <= 2 or dist <= 0:
            i = j
            continue

        segment_list.append({
            'distance': dist,
            'duration': duration,
            'start_km': total_distance / 1000
        })
        total_distance += dist
        i = j

    if not segment_list:
        return "❌ Не удалось выделить ни одного подходящего сегмента."

    total_seconds = (end_time - start_time).total_seconds()
    avg_pace_sec_per_km = total_seconds / (total_distance / 1000)

    paces = [seg['duration'] / seg['distance'] * 1000 for seg in segment_list]
    avg_pace = sum(paces) / len(paces)
    stddev = math.sqrt(sum((p - avg_pace) ** 2 for p in paces) / len(paces))

    closest_idx = min(range(len(paces)), key=lambda i: abs(paces[i] - avg_pace))
    worst_idx = max(range(len(paces)), key=lambda i: abs(paces[i] - avg_pace))

    # Формируем результат
    result = (
        "🏁 GPX-анализ завершён:\n\n"
        f"📏 Дистанция: {total_distance / 1000:.2f} км\n"
        f"⏱️ Время: {int(total_seconds // 60):02d}:{int(total_seconds % 60):02d}\n"
        f"🚀 Средний темп: {format_pace(avg_pace_sec_per_km)} /км\n"
        f"📊 СКО темпа: {pace_difference(stddev)} /км\n\n"
        f"🎯 Самый стабильный отрезок:\n"
        f"— Отметка: {segment_list[closest_idx]['start_km']:.2f} км\n"
        f"— Темп: {format_pace(paces[closest_idx])} /км\n"
        f"— Отклонение: {pace_difference(paces[closest_idx] - avg_pace)}\n\n"
        f"⚠️ Самый нестабильный отрезок:\n"
        f"— Отметка: {segment_list[worst_idx]['start_km']:.2f} км\n"
        f"— Темп: {format_pace(paces[worst_idx])} /км\n"
        f"— Отклонение: {pace_difference(paces[worst_idx] - avg_pace)}"
    )
    return result
