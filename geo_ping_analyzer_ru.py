import subprocess
import time
import sys
from datetime import datetime
import statistics

# --- КОНФИГУРАЦИЯ ---
# Список глобальных целей с известными приблизительными географическими координатами
# Используются надежные публичные DNS-серверы для максимально широкого географического охвата (весь мир).
TARGETS = {
    # Северная Америка
    "Google_US_E": {"ip": "8.8.8.8", "location": "Вирджиния/Калифорния, США (Северная Америка)"},
    "OpenDNS_US_W": {"ip": "208.67.222.222", "location": "Сан-Франциско, США (Запад)"},
    
    # Южная Америка
    "Google_BR": {"ip": "8.8.4.4", "location": "Сан-Паулу, Бразилия (Южная Америка)"},
    
    # Европа
    "Cloudflare_EU": {"ip": "1.1.1.1", "location": "Франкфурт/Лондон, Германия/Великобритания (Европа)"},
    "Quad9_EU": {"ip": "9.9.9.9", "location": "Цюрих/Амстердам (Европа)"},
    "Yandex_RU": {"ip": "77.88.8.8", "location": "Москва, Россия (Евразия)"},
    
    # Африка
    "OpenDNS_ZA": {"ip": "196.43.46.190", "location": "Йоханнесбург, ЮАР (Африка)"},
    
    # Азия (Восток и Юго-Восток)
    "AliDNS_CN": {"ip": "223.5.5.5", "location": "Пекин/Шанхай, Китай (Восточная Азия)"},
    "Hinet_TW": {"ip": "168.95.1.1", "location": "Тайбэй, Тайвань (Восточная Азия)"},
    
    # Океания/Австралия
    "Cloudflare_AU": {"ip": "1.0.0.1", "location": "Сидней, Австралия (Океания)"},
}

# Количество пакетов для отправки на каждую цель
PING_COUNT = 3
# Таймаут для каждого отдельного пакета (в секундах)
PING_TIMEOUT_PER_PACKET = 2 
# Общий таймаут для выполнения команды (должен быть больше, чем PING_COUNT * PING_TIMEOUT_PER_PACKET)
COMMAND_TIMEOUT = (PING_COUNT * PING_TIMEOUT_PER_PACKET) + 5 

# --- ФУНКЦИЯ ДЛЯ ПИНГА ОДНОЙ ЦЕЛИ ---
def ping_target(target_name, target_data):
    """Выполняет серию пингов и возвращает статистику."""
    ip = target_data['ip']
    
    # Добавляем опцию таймаута на пакет (-W 2) для большей надежности и -c для количества пакетов
    PING_COMMAND = ['ping', '-c', str(PING_COUNT), '-W', str(PING_TIMEOUT_PER_PACKET), ip]
    
    latencies = []
    loss = 0
        
    try:
        # Запускаем команду ping. Используем увеличенный таймаут для всей команды.
        result = subprocess.run(
            PING_COMMAND, 
            capture_output=True, 
            text=True, 
            timeout=COMMAND_TIMEOUT
        )
        
        # Разбираем вывод ping
        
        # 1. Поиск потерь
        loss_line = [line for line in result.stdout.split('\n') if 'transmitted' in line]
        if loss_line:
            # Пример: 3 packets transmitted, 2 received, 33% packet loss, time 2005ms
            parts = loss_line[0].split(', ')
            for part in parts:
                if 'loss' in part:
                    # Извлекаем процент потерь
                    loss_percent_str = part.split()[0].replace('%', '')
                    loss_percent = float(loss_percent_str)
                    received_count = PING_COUNT - int(PING_COUNT * loss_percent / 100)
                    loss = PING_COUNT - received_count
                    
        # 2. Поиск времени (латентности)
        rtt_line = [line for line in result.stdout.split('\n') if 'min/avg/max' in line]
        if rtt_line:
            # Пример: rtt min/avg/max/mdev = 44.130/45.289/46.853/1.121 ms
            # Берем только среднее значение (avg)
            avg_latency = float(rtt_line[0].split('=')[1].split('/')[1])
            latencies.append(avg_latency)
            
        # Если не удалось найти среднее время или все пакеты потеряны, 
        # возвращаем "Бесконечность" и полный процент потерь.
        if not latencies or loss == PING_COUNT:
            return float('inf'), 100.0, PING_COUNT, loss

        return latencies[0], loss_percent, PING_COUNT, loss
        
    except subprocess.TimeoutExpired:
        # Общий таймаут команды
        return float('inf'), 100.0, PING_COUNT, PING_COUNT
    except Exception as e:
        # Другие ошибки (например, хост недоступен)
        # print(f"Ошибка при пинге {target_name}: {e}", file=sys.stderr)
        return float('inf'), 100.0, PING_COUNT, PING_COUNT

# --- ГЛАВНАЯ ФУНКЦИЯ АНАЛИЗА ---
def run_geo_analyzer():
    start_time = datetime.now()
    results = {}
    
    print("🌍 Запуск гео-анализатора PING...")
    print(f"   Проверяем {len(TARGETS)} глобальных целей. Отправляется {PING_COUNT} пакета на каждую цель.")
    print("=" * 80)
    
    # 1. Выполнение пингов
    for name, data in TARGETS.items():
        avg_latency, loss_percent, transmitted, lost = ping_target(name, data)
        
        results[name] = {
            'ip': data['ip'],
            'location': data['location'],
            'avg_latency': avg_latency,
            'loss_percent': loss_percent,
            'transmitted': transmitted,
            'lost': lost
        }
        
        status = "✅ OK" if avg_latency != float('inf') else "❌ FAIL"
        latency_str = f"{avg_latency:.2f} мс" if avg_latency != float('inf') else "TIMEOUT"
        
        print(f"[{status}] {name:15}: {latency_str:<12} | Потери: {loss_percent:.1f}% ({lost}/{transmitted}) | Локация: {data['location']}")
        
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("=" * 80)
    print(f"🕒 Анализ завершен за {duration:.2f} секунд.")
    
    # 2. Определение ближайшей точки
    
    # Фильтруем результаты, исключая те, которые не ответили
    responded_targets = {k: v for k, v in results.items() if v['avg_latency'] != float('inf')}
    
    if not responded_targets:
        print("\n⚠️ Внимание: Ни одна из целей не ответила на пинг. Невозможно определить географическое местоположение.")
        return

    # Находим цель с минимальной средней задержкой
    closest_target_name = min(responded_targets, key=lambda k: responded_targets[k]['avg_latency'])
    closest_target = responded_targets[closest_target_name]
    
    # 3. Вывод результатов и заключения
    print("\n================================================================================\n")
    print("⭐ ОЦЕНКА ГЕОГРАФИЧЕСКОГО МЕСТОПОЛОЖЕНИЯ ПО PING")
    print("=" * 80)
    
    print(f"На основе анализа сетевой задержки, самой БЛИЗКОЙ к Вам точкой оказалась:")
    print(f"-> ЦЕЛЬ: {closest_target_name} ({TARGETS[closest_target_name]['ip']})")
    print(f"-> ЛОКАЦИЯ: {closest_target['location']}")
    print(f"-> СРЕДНИЙ PING: {closest_target['avg_latency']:.2f} мс")
    print(f"-> ПОТЕРИ: {closest_target['loss_percent']:.1f}%")
    
    # Вывод заключения о местоположении
    print("\n✅ ЗАКЛЮЧЕНИЕ:")
    if closest_target['avg_latency'] < 50 and closest_target['loss_percent'] < 5:
        conclusion = f"Ваше сетевое соединение, вероятно, находится в том же регионе (или на том же континенте), что и {closest_target['location']}. Это подтверждается очень низкой задержкой (RTT)."
    elif closest_target['avg_latency'] < 150 and closest_target['loss_percent'] < 10:
        conclusion = f"Ваша задержка умеренная. Вы, скорее всего, находитесь на том же континенте, что и {closest_target['location']}, но на значительном расстоянии (например, в разных концах Европы/Азии)."
    elif closest_target['avg_latency'] < 300 and closest_target['loss_percent'] < 15:
        conclusion = f"Задержка высокая, но стабильная. Вероятно, Вы находитесь на другом континенте относительно {closest_target['location']}, но маршрут трафика является прямым (например, Европа -> Северная Америка)."
    else:
        # Это маловероятно, если есть цели с низкой задержкой, но служит общим выводом.
        conclusion = f"Маршрутизация трафика сложна. Самая низкая задержка ({closest_target['avg_latency']:.2f} мс) была до указанной локации, что указывает на этот регион как на наиболее близкий из доступных."
        
    print(conclusion)
    print("================================================================================")

if __name__ == "__main__":
    run_geo_analyzer()
