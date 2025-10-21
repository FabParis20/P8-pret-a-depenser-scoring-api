"""
Profiling cProfile - Analyse des goulots d'étranglement
Identifie les fonctions les plus coûteuses lors d'une prédiction
"""
import cProfile
import pstats
import io
import joblib
import pandas as pd
from pathlib import Path

# Chemins absolus depuis la racine du projet
PROJECT_ROOT = Path(__file__).parent.parent
MODEL_PATH = PROJECT_ROOT / "models" / "model.pkl"
DATA_PATH = PROJECT_ROOT / "data" / "prod" / "X_test_sample.pkl"

# Client de test
TEST_CLIENT_ID = 273460


def profile_single_prediction():
    """Profile une prédiction complète avec chargement modèle"""
    print("="*70)
    print("PROFILING cProfile - Analyse goulots d'etranglement")
    print("="*70)
    print(f"\nClient test : {TEST_CLIENT_ID}")
    print("Profiling en cours...\n")
    
    # Créer le profiler
    profiler = cProfile.Profile()
    
    # Démarrer le profiling
    profiler.enable()
    
    # CODE À PROFILER : Chargement modèle + prédiction
    model = joblib.load(MODEL_PATH)
    X_test = pd.read_pickle(DATA_PATH)
    client_data = X_test.loc[[TEST_CLIENT_ID]]
    score = model.predict_proba(client_data)[0][1]
    
    # Arrêter le profiling
    profiler.disable()
    
    print(f"Prediction terminee : score = {score:.4f}\n")
    
    # Analyser les résultats
    s = io.StringIO()
    stats = pstats.Stats(profiler, stream=s)
    
    # Trier par temps cumulatif (cumulative)
    stats.sort_stats('cumulative')
    
    # Afficher top 20 fonctions
    print("="*70)
    print("TOP 20 FONCTIONS LES PLUS COUTEUSES (temps cumulatif)")
    print("="*70)
    stats.print_stats(20)
    
    return stats, s.getvalue()


def save_profiling_results(stats_output):
    """Sauvegarder les résultats dans un fichier"""
    output_path = PROJECT_ROOT / "docs" / "profiling_results.txt"
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("RESULTATS PROFILING cProfile\n")
        f.write("="*70 + "\n\n")
        f.write(f"Client test : {TEST_CLIENT_ID}\n\n")
        f.write("TOP 20 FONCTIONS LES PLUS COUTEUSES (temps cumulatif)\n")
        f.write("-"*70 + "\n\n")
        f.write(stats_output)
    
    print(f"\nResultats sauvegardes : {output_path}")
    return output_path


def analyze_bottlenecks(stats):
    """Analyser et afficher les goulots d'étranglement principaux"""
    print("\n" + "="*70)
    print("ANALYSE DES GOULOTS D'ETRANGLEMENT")
    print("="*70)
    
    # Obtenir les statistiques
    stats_list = stats.stats
    
    # Trier par temps cumulatif
    sorted_stats = sorted(stats_list.items(), 
                         key=lambda x: x[1][3],  # cumtime
                         reverse=True)
    
    print("\nTop 5 fonctions identifiees :\n")
    
    for i, (func, (cc, nc, tt, ct, callers)) in enumerate(sorted_stats[:5], 1):
        filename, line, funcname = func
        print(f"{i}. {funcname}")
        print(f"   Fichier: {filename}:{line}")
        print(f"   Temps cumul: {ct:.4f}s ({ct*1000:.2f}ms)")
        print(f"   Appels: {nc}")
        print()
    
    # Identifier le goulot principal
    main_bottleneck = sorted_stats[0]
    func, (cc, nc, tt, ct, callers) = main_bottleneck
    filename, line, funcname = func
    
    print("-"*70)
    print("GOULOT PRINCIPAL IDENTIFIE:")
    print(f"  Fonction: {funcname}")
    print(f"  Impact: {ct:.4f}s ({(ct/sum([s[1][3] for s in sorted_stats[:10]]))*100:.1f}% du temps total)")
    print("-"*70)


if __name__ == "__main__":
    # Exécuter le profiling
    stats, output = profile_single_prediction()
    
    # Analyser les goulots
    analyze_bottlenecks(stats)
    
    # Sauvegarder les résultats
    save_profiling_results(output)
    
    print("\n" + "="*70)
    print("PROFILING TERMINE")
    print("="*70)