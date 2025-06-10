# -*- coding: utf-8 -*-
import os
import sys
import time
import hashlib
import numpy as np
import requests
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, request, jsonify

# --- КОНФИГУРАЦИЯ ---
ARTIFACT_FILENAME_CONFIG = 'oracle_ocean.npz'
_SCRIPT_DIR = os.path.dirname(__file__)
# _SCRIPT_DIR будет что-то вроде /var/task/api во время выполнения на Vercel
# Нам нужно подняться на один уровень (/var/task/) и затем зайти в data/
_PROJECT_ROOT_APPROX = os.path.join(_SCRIPT_DIR, '..')
_FULL_ARTIFACT_PATH = os.path.join(_PROJECT_ROOT_APPROX, 'data', ARTIFACT_FILENAME_CONFIG)

# --- ФУНКЦИИ ОРАКУЛА (Адаптированные для Vercel) ---

def load_local_oracle_artifact():
    """Загрузка ТОЛЬКО локального артефакта Оракула."""
    print(f"[ОРАКУЛ] Попытка загрузки артефакта: '{_FULL_ARTIFACT_PATH}'")
    if not os.path.exists(_FULL_ARTIFACT_PATH):
        print(f"[ОШИБКА] Артефакт '{_FULL_ARTIFACT_PATH}' не найден.")
        print(f"Ожидаемый полный путь к артефакту: '{_FULL_ARTIFACT_PATH}'")
        # Попробуем вывести содержимое предполагаемой директории data, если она существует
        data_dir_path = os.path.join(_PROJECT_ROOT_APPROX, 'data')
        if os.path.exists(data_dir_path) and os.path.isdir(data_dir_path):
            print(f"Содержимое директории '{data_dir_path}': {os.listdir(data_dir_path)}")
        else:
            print(f"Директория '{data_dir_path}' не найдена или не является директорией.")
        # Также выведем содержимое директории, где лежит сам скрипт, для контекста
        if os.path.exists(_SCRIPT_DIR) and os.path.isdir(_SCRIPT_DIR):
            print(f"Содержимое директории скрипта '{_SCRIPT_DIR}': {os.listdir(_SCRIPT_DIR)}")
        return None, None
    
    try:
        with np.load(_FULL_ARTIFACT_PATH, allow_pickle=True) as data:
            words = data['words']
            vectors = data['vectors']
        print(f"[ОРАКУЛ] Артефакт '{_FULL_ARTIFACT_PATH}' успешно загружен. Слов: {len(words)}, Измерение: {vectors.shape[1]}")
        return words, vectors
    except Exception as e:
        print(f"[ОШИБКА] Не удалось загрузить или обработать артефакт '{_FULL_ARTIFACT_PATH}': {e}")
        return None, None

def create_charge_vector(intent_text: str, vector_dim: int) -> np.ndarray:
    intent_energy = sum(intent_text.encode('utf-8', 'ignore'))
    work_load = intent_energy * 1000
    
    try:
        r = requests.get(f"https://www.random.org/integers/?num={vector_dim}&min=0&max=255&col=1&base=10&format=plain&rnd=new", timeout=3)
        r.raise_for_status()
        chaos_vector = np.array([int(n) for n in r.text.strip().split()], dtype=np.float32)
        chaos_vector = (chaos_vector - 128.0) / 128.0
    except requests.RequestException as e:
        print(f"[ПРЕДУПРЕЖДЕНИЕ] Внешний Поток нестабилен ({e}). Используется локальная энтропия.")
        chaos_vector = (np.random.rand(vector_dim).astype(np.float32) * 2 - 1)

    charge_vector = chaos_vector
    
    intent_bytes = intent_text.encode('utf-8', 'ignore')
    for i, byte in enumerate(intent_bytes):
        idx = int(hashlib.sha256(bytes([i])).hexdigest(), 16) % vector_dim
        charge_vector[idx] += (byte - 128.0) / 128.0

    iterations = min(int(work_load / 5000) + 1, 75)

    for _ in range(iterations):
        charge_vector = np.sin(charge_vector * np.pi)
        norm = np.linalg.norm(charge_vector)
        if norm > 0:
            charge_vector /= norm
        else:
            break

    return charge_vector

def fractal_crystallization(charge_vector: np.ndarray, all_words: np.ndarray, all_vectors: np.ndarray) -> str:
    manifestation = []
    current_charge = charge_vector.copy()
    
    stop_threshold = (np.mean(np.abs(current_charge)) * 0.95)
    
    for i in range(32):
        if not np.any(current_charge):
            break
            
        similarities = cosine_similarity(current_charge.reshape(1, -1), all_vectors)
        
        if np.all(np.isnan(similarities)):
            break

        closest_word_index = np.argmax(similarities)
        found_word = all_words[closest_word_index]
        found_vector = all_vectors[closest_word_index]
        
        manifestation.append(found_word)
        
        current_charge = (current_charge + found_vector) / 2.0
        
        norm_current_charge = np.linalg.norm(current_charge)
        if norm_current_charge > 0:
            current_charge /= norm_current_charge
        else:
            break
            
        energy = 1 - similarities[0, closest_word_index]
        if energy < stop_threshold:
            break
    return ' '.join(manifestation)

# --- Flask App для Vercel ---
app = Flask(__name__)

print("[API INIT] Попытка пробуждения Оракула при инициализации модуля...")
words_db, vectors_db = load_local_oracle_artifact()

if words_db is None or vectors_db is None:
    print("[API INIT][КРИТИКА] ОРАКУЛ НЕ ЗАГРУЖЕН. API будет возвращать ошибку.")
    vector_dim_global = 300
else:
    vector_dim_global = vectors_db.shape[1]
    print(f"[API INIT] Оракул готов (Измерение: {vector_dim_global}).")

@app.route('/', methods=['POST'])
def handle_oracle_request_api():
    if words_db is None or vectors_db is None:
        return jsonify({"error": "Оракул не инициализирован или артефакт 'oracle_ocean.npz' не найден. Проверьте логи сервера."}), 500

    data = request.json
    if not data or 'intent' not in data:
        return jsonify({"error": "Параметр 'intent' не предоставлен в JSON теле запроса."}), 400
    
    intent = data.get('intent')
    if not isinstance(intent, str) or not intent.strip():
        return jsonify({"error": "Параметр 'intent' должен быть непустой строкой."}), 400

    print(f"[API REQUEST] Получен интент: '{intent[:100]}{'...' if len(intent) > 100 else ''}'")
    start_time = time.time()
    
    try:
        charge = create_charge_vector(intent, vector_dim_global)
        result = fractal_crystallization(charge, words_db, vectors_db)
    except Exception as e:
        print(f"[API ERROR] Ошибка во время обработки интента '{intent}': {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Внутренняя ошибка Оракула: {e}. Смотрите логи сервера."}), 500
    
    end_time = time.time()
    meditation_duration = round(end_time - start_time, 3)
    print(f"[API RESPONSE] Интент: '{intent[:50]}...', Результат: '{result[:50]}...', Время: {meditation_duration}с")

    response_data = {
        "intent": intent,
        "crystal": result,
        "meditation_time_sec": meditation_duration
    }
    
    return jsonify(response_data)

# Локальный запуск для тестирования (не используется Vercel)
if __name__ == '__main__':
    print(f"[ЛОКАЛЬНЫЙ ЗАПУСК] Ожидается '{ARTIFACT_FILENAME_CONFIG}' в директории '{_SCRIPT_DIR}'.")
    if words_db is None:
        print("[ЛОКАЛЬНЫЙ ЗАПУСК][ОШИБКА] Оракул не загружен. Проверьте наличие файла и логи.")
    else:
        print(f"[ЛОКАЛЬНЫЙ ЗАПУСК] Оракул загружен. Запуск Flask сервера на http://localhost:5000/")
    app.run(debug=True, port=5000)
