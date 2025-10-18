"""
Script de validation du chargement des assets de production.
Vérifie que le modèle et les données sont correctement chargés.
"""
import pickle
from pathlib import Path
import pandas as pd

# Chemins des fichiers
PROJECT_ROOT = Path(__file__).parent
MODEL_PATH = PROJECT_ROOT / "models" / "model.pkl"
DATA_TEST_PATH = PROJECT_ROOT / "data" / "prod" / "X_test_sample.pkl"

print("="*60)
print("🔍 VALIDATION DES ASSETS DE PRODUCTION")
print("="*60)

# === VÉRIFICATION PRÉSENCE DES FICHIERS ===
print("\n📂 Vérification de la présence des fichiers...")

files_to_check = {
    "Modèle": MODEL_PATH,
    "Données test": DATA_TEST_PATH
}

all_present = True
for name, path in files_to_check.items():
    if path.exists():
        print(f"   ✅ {name} : {path.name}")
    else:
        print(f"   ❌ {name} MANQUANT : {path}")
        all_present = False

if not all_present:
    print("\n❌ Des fichiers sont manquants. Arrêt du script.")
    exit(1)

print("\n✅ Tous les fichiers sont présents")

# === CHARGEMENT DU MODÈLE ===
print("\n🤖 Chargement du modèle...")

try:
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    print("   ✅ Modèle chargé avec succès")
except Exception as e:
    print(f"   ❌ Erreur lors du chargement : {e}")
    exit(1)

# Vérifier le type
print(f"\n📋 Type du modèle : {type(model).__name__}")

# Vérifier si c'est un Pipeline
if hasattr(model, 'steps'):
    print("   ✅ C'est un Pipeline sklearn")
    print("\n   Étapes du pipeline :")
    for name, step in model.steps:
        print(f"      - {name}: {type(step).__name__}")
else:
    print("   ℹ️  C'est un modèle simple (pas un Pipeline)")

# === VÉRIFICATION NOMBRE DE FEATURES ===
print("\n📊 Vérification des features du modèle...")

# Accéder au classificateur (dernière étape du pipeline)
classifier = model.named_steps['clf']

# Nombre de features attendues
n_features = classifier.n_features_in_

print(f"   Features attendues par le modèle : {n_features}")

if n_features == 813:
    print("   ✅ Correspond au nombre attendu (813)")
else:
    print(f"   ⚠️ Différence détectée ! Attendu : 813, Trouvé : {n_features}")

# === VÉRIFICATION NOMBRE DE FEATURES ===
print("\n📊 Vérification des features du modèle...")

# Accéder au classificateur (dernière étape du pipeline)
classifier = model.named_steps['clf']

# Nombre de features attendues (après preprocessing)
n_features = classifier.n_features_in_

print(f"   Features attendues par le modèle : {n_features}")
print(f"   ✅ Le modèle attend les données APRÈS preprocessing")
print(f"      (OneHotEncoding transforme 813 colonnes → {n_features} features)")

# === CHARGEMENT DES DONNÉES ===
print("\n📊 Chargement des données de test...")

try:
    X_test_sample = pd.read_pickle(DATA_TEST_PATH)
    print(f"   ✅ X_test_sample chargé : {X_test_sample.shape}")
except Exception as e:
    print(f"   ❌ Erreur lors du chargement : {e}")
    exit(1)

# Vérifier que le modèle a feature_names_in_
if hasattr(model, 'feature_names_in_'):
    model_features = model.feature_names_in_
    data_features = X_test_sample.columns.tolist()
    
    print(f"\n🔍 Vérification alignement des colonnes...")
    
    if list(model_features) == data_features:
        print("   ✅ Les colonnes sont parfaitement alignées")
    else:
        print("   ⚠️ Différence dans l'ordre ou les noms des colonnes")
        
else:
    print("\n   ℹ️  Le modèle n'expose pas feature_names_in_ (normal pour un Pipeline)")
    print("   ✅ On fait confiance au preprocessing du Pipeline")

# === TEST DE PRÉDICTIONS ===
print("\n🧪 Test de prédictions sur 3 clients aléatoires...")

# Sélectionner 3 clients au hasard
import numpy as np
np.random.seed(54)
random_indices = np.random.choice(len(X_test_sample), size=3, replace=False)

print(f"   Indices sélectionnés : {random_indices.tolist()}")

# Faire les prédictions
try:
    X_sample = X_test_sample.iloc[random_indices]
    predictions = model.predict_proba(X_sample)
    
    print("\n   Résultats :")
    for i, (idx, pred) in enumerate(zip(random_indices, predictions)):
        client_id = X_test_sample.index[idx]
        proba_classe_1 = pred[1]  # Probabilité de défaut
        
        print(f"      Client {client_id} → Proba défaut : {proba_classe_1:.4f}")
    
    print("\n   ✅ Les prédictions fonctionnent correctement")
    
except Exception as e:
    print(f"   ❌ Erreur lors des prédictions : {e}")
    exit(1)

# === IDENTIFICATION CLIENTS DÉMO ===
print("\n🎯 Identification de 10 clients de démo...")

# Seuil de décision du Projet 6
THRESHOLD = 0.10

# Prédire sur tout l'échantillon
all_predictions = model.predict_proba(X_test_sample)
probas_defaut = all_predictions[:, 1]

# Créer un DataFrame SÉPARÉ pour les résultats
results = pd.DataFrame({
    'client_id': X_test_sample.index,
    'proba_defaut': probas_defaut
})

results['decision'] = results['proba_defaut'].apply(
    lambda p: 'REFUSE' if p > THRESHOLD else 'ACCEPTE'
)

print(f"   Seuil de décision : {THRESHOLD}")
print(f"   Total clients : {len(results)}")
print(f"   Acceptés : {(results['decision'] == 'ACCEPTE').sum()}")
print(f"   Refusés : {(results['decision'] == 'REFUSE').sum()}")
print(X_test_sample.shape)  # Devrait afficher (2000, 813)
print(X_test_sample.columns[-5:])

# === SÉLECTION DES 10 CLIENTS DÉMO ===
print("\n📋 Sélection de 10 clients de démo...")

# Séparer acceptés et refusés
acceptes = results[results['decision'] == 'ACCEPTE'].sort_values('proba_defaut')
refuses = results[results['decision'] == 'REFUSE'].sort_values('proba_defaut')

# Prendre 5 de chaque catégorie avec des scores variés
# Pour les acceptés : du plus sûr au plus limite
demo_acceptes = acceptes.iloc[[0, 300, 600, 900, -1]]

# Pour les refusés : du plus limite au plus risqué
demo_refuses = refuses.iloc[[0, 100, 200, 300, -1]]

print(f"\n✅ 5 clients ACCEPTÉS (proba < 0.10) :")
for _, row in demo_acceptes.iterrows():
    print(f"   Client {row['client_id']} → {row['proba_defaut']:.4f}")

print(f"\n❌ 5 clients REFUSÉS (proba > 0.10) :")
for _, row in demo_refuses.iterrows():
    print(f"   Client {row['client_id']} → {row['proba_defaut']:.4f}")

# === SAUVEGARDE DES CLIENTS DÉMO ===
print("\n💾 Sauvegarde des clients de démo...")

# Combiner les deux listes
demo_clients = pd.concat([demo_acceptes, demo_refuses])

# Créer le fichier Markdown
demo_file = PROJECT_ROOT / "demo_clients.md"

with open(demo_file, 'w', encoding='utf-8') as f:
    f.write("# Clients de démonstration\n\n")
    f.write("Liste de 10 clients sélectionnés pour tester l'API en production.\n\n")
    f.write(f"**Seuil de décision** : {THRESHOLD}\n\n")
    
    f.write("## ✅ Clients ACCEPTÉS (5)\n\n")
    f.write("| Client ID | Probabilité défaut | Score |\n")
    f.write("|-----------|-------------------|-------|\n")
    for _, row in demo_acceptes.iterrows():
        f.write(f"| {row['client_id']} | {row['proba_defaut']:.4f} | Faible risque |\n")
    
    f.write("\n## ❌ Clients REFUSÉS (5)\n\n")
    f.write("| Client ID | Probabilité défaut | Score |\n")
    f.write("|-----------|-------------------|-------|\n")
    for _, row in demo_refuses.iterrows():
        f.write(f"| {row['client_id']} | {row['proba_defaut']:.4f} | Risque élevé |\n")

print(f"   ✅ Fichier créé : {demo_file.name}")
print(f"\n📍 Les IDs sont maintenant sauvegardés dans demo_clients.md")# === SAUVEGARDE DES CLIENTS DÉMO ===
print("\n💾 Sauvegarde des clients de démo...")

# Combiner les deux listes
demo_clients = pd.concat([demo_acceptes, demo_refuses])

# Créer le fichier Markdown
demo_file = PROJECT_ROOT / "demo_clients.md"

with open(demo_file, 'w', encoding='utf-8') as f:
    f.write("# Clients de démonstration\n\n")
    f.write("Liste de 10 clients sélectionnés pour tester l'API en production.\n\n")
    f.write(f"**Seuil de décision** : {THRESHOLD}\n\n")
    
    f.write("## ✅ Clients ACCEPTÉS (5)\n\n")
    f.write("| Client ID | Probabilité défaut | Score |\n")
    f.write("|-----------|-------------------|-------|\n")
    for _, row in demo_acceptes.iterrows():
        f.write(f"| {row['client_id']} | {row['proba_defaut']:.4f} | Faible risque |\n")
    
    f.write("\n## ❌ Clients REFUSÉS (5)\n\n")
    f.write("| Client ID | Probabilité défaut | Score |\n")
    f.write("|-----------|-------------------|-------|\n")
    for _, row in demo_refuses.iterrows():
        f.write(f"| {row['client_id']} | {row['proba_defaut']:.4f} | Risque élevé |\n")

print(f"   ✅ Fichier créé : {demo_file.name}")
print(f"\n📍 Les IDs sont maintenant sauvegardés dans demo_clients.md")