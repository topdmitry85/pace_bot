import gpxpy
import gpxpy.gpx
from datetime import timedelta
import matplotlib.pyplot as plt
import io

SEGMENT_LENGTH_METERS = 20

def format_pace(seconds_per_km):
    if seconds_per_km == 0:
        return "0:00"
    minutes = int(seconds_per_km // 60)
    seconds = int(seconds_per_km % 60)
    return f"{minutes}:{seconds:02d}"

def plot_pace_graph(segment_paces, avg_pace):
    plt.figure(figsize=(10, 4))
    x = [i * SEGMENT_LENGTH_METERS / 1000 for i in range(len(segment_paces))]
    plt.plot(x, segment_paces, label='Темп (с/км)', color='blue')
    plt.axhline(avg_pace, color='red', linestyle='--', label='Средний темп')
    plt.xlabel('Дистанция (км)')
    plt.ylabel('Темп (с/км)')
    plt.title('График темпа по отрезкам')
    plt.legend()
    plt.grid(True)
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()
    return buffer

def process_gpx_file(file_path):
    with open(file_path, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    all_points = []

    for track in gpx.tracks:
        for segment in track.segments:
            all_points.extend(segment.points)

    if len(all_points) < 2:
        return "❌ Недостаточно данных в GPX-файле.", None

    total_distance = 0
    total_time = 0
    segment_paces = []
    segment_dist = 0
    segment_time = 0

    previous_point = all_points[0]
    start_time = previous_point.time
    end_time = previous_point.time

    for point in all_points[1:]:
        dist = point.distance_3d(previous_point) or 0
        time_diff = (point.time - previous_point.time).total_seconds() if point.time and previous_point.time else 0

        total_distance += dist
        total_time += time_diff
        segment_dist += dist
        segment_time += time_diff
        end_time = point.time

        if segment_dist >= SEGMENT_LENGTH_METERS:
            pace = segment_time / (segment_dist / 1000)  # сек/км
            segment_paces.append(pace)
            segment_dist = 0
            segment_time = 0

        previous_point = point

    # Учет последнего неполного сегмента
    if segment_dist > 0 and segment_time > 0:
        pace = segment_time / (segment_dist / 1000)
        segment_paces.append(pace)

    if total_distance == 0 or total_time == 0:
        return "❌ Ошибка: невозможно вычислить параметры.", None

    avg_pace = total_time / (total_distance / 1000)
    pace_diffs = [(p - avg_pace) ** 2 for p in segment_paces]
    std_dev = (sum(pace_diffs) / len(pace_diffs)) ** 0.5 if pace_diffs else 0

    # Поиск самого стабильного и нестабильного отрезков
    deviations = [abs(p - avg_pace) for p in segment_paces]
    min_dev = min(deviations) if deviations else 0
    max_dev = max(deviations) if deviations else 0
    min_index = deviations.index(min_dev) if deviations else 0
    max_index = deviations.index(max_dev) if deviations else 0

    min_pace = segment_paces[min_index] if segment_paces else 0
    max_pace = segment_paces[max_index] if segment_paces else 0

    distance_km = total_distance / 1000

    image_buffer = plot_pace_graph(segment_paces, avg_pace)

    report = f"""
🏁 GPX-анализ завершён:
📏 Дистанция: {distance_km:.2f} км
⏱️ Время: {int(total_time // 60):02d}:{int(total_time % 60):02d}
⚖️ Средний темп: {format_pace(avg_pace)} /км
📊 СКО темпа: {format_pace(std_dev)} /км

🎯 Самый стабильный отрезок:
— Отметка {min_index * SEGMENT_LENGTH_METERS / 1000:.2f} км
— Темп: {format_pace(min_pace)} /км
— Отклонение: ±{format_pace(min_dev)} /км

⚠️ Самый нестабильный отрезок:
— Отметка {max_index * SEGMENT_LENGTH_METERS / 1000:.2f} км
— Темп: {format_pace(max_pace)} /км
— Отклонение: ±{format_pace(max_dev)} /км
""".strip()

    return report, image_buffer
