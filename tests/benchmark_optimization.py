"""
Benchmark des optimisations API - Version minimale
Compare chargement modèle à chaque requête vs préchargement
"""
import time
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Chemins ABSOLUS depuis la racine du projet
PROJECT_ROOT = Path(__file__).parent.parent
MODEL_PATH = PROJECT_ROOT / "models" / "model.pkl"
DATA_PATH = PROJECT_ROOT / "data" / "prod" / "X_test_sample.pkl"

# Client de test
TEST_CLIENT_ID = 273460
N_ITERATIONS = 50

def benchmark_naive():
    """Version NAIVE : Charger modèle à chaque prédiction"""
    print("🔴 Benchmark VERSION NAIVE (rechargement modèle)...")
    
    times = []
    X_test = pd.read_pickle(DATA_PATH)
    
    for i in range(N_ITERATIONS):
        start = time.perf_counter()
        
        # Simuler rechargement modèle
        model = joblib.load(MODEL_PATH)
        client_data = X_test.loc[[TEST_CLIENT_ID]]
        score = model.predict_proba(client_data)[0][1]
        
        elapsed = (time.perf_counter() - start) * 1000  # en ms
        times.append(elapsed)
        
        if (i + 1) % 10 == 0:
            print(f"  Progression : {i+1}/{N_ITERATIONS}")
    
    return times

def benchmark_optimized():
    """Version OPTIMISÉE : Préchargement modèle"""
    print("\n🟢 Benchmark VERSION OPTIMISÉE (préchargement)...")
    
    times = []
    
    # Précharger AVANT la boucle
    model = joblib.load(MODEL_PATH)
    X_test = pd.read_pickle(DATA_PATH)
    
    for i in range(N_ITERATIONS):
        start = time.perf_counter()
        
        # Utiliser modèle déjà chargé
        client_data = X_test.loc[[TEST_CLIENT_ID]]
        score = model.predict_proba(client_data)[0][1]
        
        elapsed = (time.perf_counter() - start) * 1000  # en ms
        times.append(elapsed)
        
        if (i + 1) % 10 == 0:
            print(f"  Progression : {i+1}/{N_ITERATIONS}")
    
    return times

def print_results(naive_times, optimized_times):
    """Afficher tableau comparatif"""
    print("\n" + "="*70)
    print("📊 RÉSULTATS BENCHMARK OPTIMISATIONS")
    print("="*70)
    
    naive_mean = np.mean(naive_times)
    opt_mean = np.mean(optimized_times)
    gain = ((naive_mean - opt_mean) / naive_mean) * 100
    
    print(f"\n{'Métrique':<25} {'Naive (ms)':<15} {'Optimisé (ms)':<15} {'Gain':>10}")
    print("-"*70)
    print(f"{'Temps moyen':<25} {naive_mean:>10.2f}     {opt_mean:>10.2f}     {gain:>7.1f}%")
    print(f"{'Temps médian':<25} {np.median(naive_times):>10.2f}     {np.median(optimized_times):>10.2f}")
    print(f"{'P95 (95e percentile)':<25} {np.percentile(naive_times, 95):>10.2f}     {np.percentile(optimized_times, 95):>10.2f}")
    print(f"{'P99 (99e percentile)':<25} {np.percentile(naive_times, 99):>10.2f}     {np.percentile(optimized_times, 99):>10.2f}")
    print(f"{'Temps min':<25} {np.min(naive_times):>10.2f}     {np.min(optimized_times):>10.2f}")
    print(f"{'Temps max':<25} {np.max(naive_times):>10.2f}     {np.max(optimized_times):>10.2f}")
    print(f"{'Écart-type':<25} {np.std(naive_times):>10.2f}     {np.std(optimized_times):>10.2f}")
    
    print("\n" + "="*70)
    print(f"✅ GAIN PERFORMANCE : {gain:.1f}% (facteur {naive_mean/opt_mean:.1f}x)")
    print("="*70)

if __name__ == "__main__":
    print(f"🧪 Benchmark sur {N_ITERATIONS} prédictions (client {TEST_CLIENT_ID})\n")
    
    naive_times = benchmark_naive()
    optimized_times = benchmark_optimized()
    
    print_results(naive_times, optimized_times)
    
    # Sauvegarder résultats
    output_path = PROJECT_ROOT / "docs" / "benchmark_results.txt"
    output_path.parent.mkdir(exist_ok=True)  # Créer docs/ si n'existe pas
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("RÉSULTATS BENCHMARK OPTIMISATIONS\n")
        f.write("="*70 + "\n\n")
        f.write(f"Iterations : {N_ITERATIONS}\n")
        f.write(f"Client test : {TEST_CLIENT_ID}\n\n")
        f.write(f"Temps moyen naive : {np.mean(naive_times):.2f} ms\n")
        f.write(f"Temps moyen optimisé : {np.mean(optimized_times):.2f} ms\n")
        f.write(f"Gain performance : {((np.mean(naive_times) - np.mean(optimized_times)) / np.mean(naive_times)) * 100:.1f}%\n")
    
    print(f"\n💾 Résultats sauvegardés : {output_path}")