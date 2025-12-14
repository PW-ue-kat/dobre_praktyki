# ==============================================================================
# PROJEKT: Testowanie i Optymalizacja Sieci CNN (Dataset: Flower Photos)
# ==============================================================================

import matplotlib.pyplot as plt
import numpy as np
import os
import shutil
import tensorflow as tf
import time
import pandas as pd
from tensorflow.keras import layers, models, applications
from tensorflow.keras.utils import get_file
from clearml import Task
import datetime

# Inicjalizacja projektu MLOps
# To musi być PIERWSZA linijka kodu wykonawczego
task = Task.init(project_name="Projekt CNN", task_name="Zbiorczy Raport Eksperymentow")

# Ustawienia globalne
BATCH_SIZE_DEFAULT = 32
IMG_SIZE_DEFAULT = (160, 160) # Uśredniony rozmiar dla szybkości
EPOCHS = 4  # Mała liczba epok, aby projekt policzył się w rozsądnym czasie na zajęciach
BASE_DIR = 'project_data'
MAIN_DATA_DIR = os.path.join(BASE_DIR, 'train_data')
RESERVE_DATA_DIR = os.path.join(BASE_DIR, 'reserve_data')

# ==============================================================================
# 1. PRZYGOTOWANIE DANYCH (Wymaganie: Baza danych wieloklasowa)
# ==============================================================================
def prepare_environment():
    print("--- 1. Pobieranie i przygotowanie danych (Flower Photos) ---")

    # Pobieranie
    dataset_url = "https://storage.googleapis.com/download.tensorflow.org/example_images/flower_photos.tgz"
    archive = get_file("flower_photos.tgz", origin=dataset_url, extract=True)
    # Poprawka: 'flower_photos' jest często zagnieżdżone w folderze ekstrahowanym przez get_file
    source_dir = os.path.join(archive, 'flower_photos')

    # Czyszczenie środowiska
    if os.path.exists(BASE_DIR):
        shutil.rmtree(BASE_DIR)
    os.makedirs(MAIN_DATA_DIR)
    os.makedirs(RESERVE_DATA_DIR)

    # Lista klas (folderów)
    classes = ['daisy', 'dandelion', 'roses', 'sunflowers', 'tulips']

    # Podział na dane główne i "rezerwowe" (do punktu 4d - dokładanie danych)
    for cls in classes:
        src_cls_path = os.path.join(source_dir, cls)
        dst_main_path = os.path.join(MAIN_DATA_DIR, cls)
        dst_res_path = os.path.join(RESERVE_DATA_DIR, cls)

        os.makedirs(dst_main_path, exist_ok=True)
        os.makedirs(dst_res_path, exist_ok=True)

        files = os.listdir(src_cls_path)
        # 80% idzie na start, 20% chowamy do rezerwy
        split_index = int(len(files) * 0.8)

        for f in files[:split_index]:
            shutil.copy(os.path.join(src_cls_path, f), os.path.join(dst_main_path, f))
        for f in files[split_index:]:
            shutil.copy(os.path.join(src_cls_path, f), os.path.join(dst_res_path, f))

    print(f"Dane gotowe. Treningowe: {MAIN_DATA_DIR}, Rezerwowe: {RESERVE_DATA_DIR}")

# ==============================================================================
# 2. FUNKCJE POMOCNICZE (Ładowanie i Trening)
# ==============================================================================

def get_dataset(data_dir, img_size, batch_size, augment=False):
    # Augmentacja danych (Wymaganie 4b)
    data_augmentation = tf.keras.Sequential([
        layers.RandomFlip("horizontal"),
        layers.RandomRotation(0.2),
        layers.RandomZoom(0.2),
    ]) if augment else None

    # Ładowanie z katalogu
    train_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=0.2,
        subset="training",
        seed=123,
        image_size=img_size,
        batch_size=batch_size,
        verbose=0
    )

    val_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=0.2,
        subset="validation",
        seed=123,
        image_size=img_size,
        batch_size=batch_size,
        verbose=0
    )

    if augment:
        train_ds = train_ds.map(lambda x, y: (data_augmentation(x, training=True), y))

    # Optymalizacja wydajności (prefetch)
    train_ds = train_ds.cache().prefetch(buffer_size=tf.data.AUTOTUNE)
    val_ds = val_ds.cache().prefetch(buffer_size=tf.data.AUTOTUNE)

    return train_ds, val_ds


def run_experiment(name, model_name='ResNet50', transfer_learning=True,
                   device='/GPU:0', normalize=True, dropout=0.0,
                   augment=False, img_size=IMG_SIZE_DEFAULT,
                   batch_size=BATCH_SIZE_DEFAULT, data_path=MAIN_DATA_DIR):
    print(f"Eksperyment: {name}...")

    # 1. Przygotowanie danych
    train_ds, val_ds = get_dataset(data_path, img_size, batch_size, augment)

    # 2. Wybór architektury
    base_models = {
        'ResNet50': applications.ResNet50,
        'VGG16': applications.VGG16,
        'InceptionV3': applications.InceptionV3,
        'MobileNet': applications.MobileNet
    }
    BaseModel = base_models.get(model_name, applications.ResNet50)

    try:
        with tf.device(device):
            inputs = tf.keras.Input(shape=img_size + (3,))
            x = inputs
            if normalize:
                x = layers.Rescaling(1. / 255)(x)

            weights = 'imagenet' if transfer_learning else None
            base_model = BaseModel(include_top=False, weights=weights, input_tensor=x)

            if transfer_learning:
                base_model.trainable = False

            x = base_model.output
            x = layers.GlobalAveragePooling2D()(x)
            if dropout > 0:
                x = layers.Dropout(dropout)(x)

            outputs = layers.Dense(5, activation='softmax')(x)
            model = tf.keras.Model(inputs, outputs)

            model.compile(optimizer='adam',
                          loss='sparse_categorical_crossentropy',
                          metrics=['accuracy'])

            # --- POPRAWKA DLA CLEARML ---
            # Tworzymy unikalny folder logów dla każdego eksperymentu
            log_dir = "logs/fit/" + name.replace(" ", "_").replace(".", "") + "_" + datetime.datetime.now().strftime(
                "%Y%m%d-%H%M%S")
            tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)

            start_time = time.time()

            # Dodajemy callback do model.fit
            # verbose=1 żebyś widział pasek postępu w PyCharm (ważne na CPU!)
            history = model.fit(train_ds,
                                validation_data=val_ds,
                                epochs=EPOCHS,
                                verbose=1,
                                callbacks=[tensorboard_callback])
            end_time = time.time()

    except RuntimeError as e:
        print(f"Błąd urządzenia {device}: {e}")
        return None

    duration = end_time - start_time
    best_acc = max(history.history['val_accuracy'])

    # --- RAPORTOWANIE ZBIORCZE DO CLEARML ---
    logger = Task.current_task().get_logger()

    # Raportujemy końcowe wyniki na wykresy porównawcze
    logger.report_scalar(title='Porównanie Dokładności', series='Val Accuracy', value=best_acc, iteration=len(results))
    logger.report_scalar(title='Porównanie Czasu', series='Czas Treningu [s]', value=duration, iteration=len(results))

    print(f"   -> Czas: {duration:.1f}s | Dokładność (Val): {best_acc:.2%}")

    return {
        'Nazwa': name,
        'Czas [s]': duration,
        'Dokładność': best_acc,
        'Kategoria': 'Inne'
    }


# ==============================================================================
# 3. GŁÓWNA PĘTLA EKSPERYMENTÓW
# ==============================================================================

prepare_environment()
results = []

# --- A. BASELINE (Wymaganie 2) ---
# Uwaga: ResNet od zera na CPU trwa bardzo długo, dajemy tu mało epok pokazowo.
print("\n--- BASELINE (CPU vs GPU) ---")
results.append(run_experiment("1. Baseline (CPU, Scratch)", device='/CPU:0', transfer_learning=False))
results[-1]['Kategoria'] = 'Sprzęt'

# --- B. GPU & TRANSFER LEARNING (Wymaganie 3a, 3b) ---
results.append(run_experiment("2. GPU (Scratch)", device='/GPU:0', transfer_learning=False))
results[-1]['Kategoria'] = 'Sprzęt'

results.append(run_experiment("3. Transfer Learning (GPU)", device='/GPU:0', transfer_learning=True))
results[-1]['Kategoria'] = 'Metoda'

# --- C. OPTYMALIZACJA DOKŁADNOŚCI (Wymaganie 4) ---
print("\n--- OPTYMALIZACJA ---")

# Normalizacja (Wymaganie 4a)
# Uwaga: Nasza funkcja domyślnie ma normalize=True, więc testujemy brak.
results.append(run_experiment("4. Bez Normalizacji", normalize=False))
results[-1]['Kategoria'] = 'Preprocessing'

# Augmentacja (Wymaganie 4b)
results.append(run_experiment("5. Z Augmentacją", augment=True))
results[-1]['Kategoria'] = 'Preprocessing'

# Dropout (Wymaganie 4c)
results.append(run_experiment("6. Z Dropout (0.5)", dropout=0.5))
results[-1]['Kategoria'] = 'Regularyzacja'

# --- D. DOKŁADANIE DANYCH (Wymaganie 4d) ---
print("\n--- DOKŁADANIE DANYCH ---")
# Krok 1: Przenosimy dane z rezerwy do głównego folderu
print("   -> Przenoszenie danych z rezerwy...")
for folder in os.listdir(RESERVE_DATA_DIR):
    src = os.path.join(RESERVE_DATA_DIR, folder)
    dst = os.path.join(MAIN_DATA_DIR, folder)
    for f in os.listdir(src):
        shutil.copy(os.path.join(src, f), os.path.join(dst, f))

# Krok 2: Trenujemy ponownie na większym zbiorze
results.append(run_experiment("7. Po dołożeniu danych", data_path=MAIN_DATA_DIR))
results[-1]['Kategoria'] = 'Dane'

# --- E. ROZMIARY WEJŚCIOWE (Wymaganie 4e) ---
print("\n--- ROZMIARY WEJŚCIOWE ---")
sizes = [96, 160, 224]
for s in sizes:
    res = run_experiment(f"8. Rozmiar {s}x{s}", img_size=(s, s))
    res['Kategoria'] = 'Rozmiar Obrazu'
    results.append(res)

# --- F. BATCH SIZE (Wymaganie 4f) ---
print("\n--- BATCH SIZE ---")
batches = [32, 64, 128]
for b in batches:
    res = run_experiment(f"9. Batch Size {b}", batch_size=b)
    res['Kategoria'] = 'Batch Size'
    results.append(res)

# --- G. STRUKTURY SIECI (Wymaganie 4g) ---
print("\n--- ARCHITEKTURY SIECI ---")
nets = ['VGG16', 'InceptionV3', 'MobileNet'] # ResNet już był
for net in nets:
    res = run_experiment(f"10. Sieć {net}", model_name=net, img_size=(160, 160)) # Inception wymaga >75px
    res['Kategoria'] = 'Architektura'
    results.append(res)

# ==============================================================================
# 4. RAPORTOWANIE I WYKRESY
# ==============================================================================
print("\n--- GENEROWANIE RAPORTÓW ---")
df = pd.DataFrame(results)

# Wyświetlenie tabeli
print(df[['Nazwa', 'Czas [s]', 'Dokładność']])

# Funkcja rysująca
def plot_metric(metric_col, title, color):
    plt.figure(figsize=(14, 8))
    # Sortowanie, żeby wykres był czytelny
    df_sorted = df.sort_values(by=metric_col, ascending=(metric_col == 'Czas [s]'))

    plt.barh(df_sorted['Nazwa'], df_sorted[metric_col], color=color)
    plt.xlabel(metric_col)
    plt.title(title)
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

# Wykres 1: Czas treningu
plot_metric('Czas [s]', 'Porównanie Czasu Treningu (mniej = lepiej)', 'salmon')

# Wykres 2: Dokładność
plot_metric('Dokładność', 'Porównanie Dokładności Walidacyjnej (więcej = lepiej)', 'skyblue')

print("Zakończono. Możesz pobrać notebook jako raport.")