"""
Script de simulation de requêtes API
Génère 100 prédictions pour alimenter les logs de production
"""

import requests
import time
import random

# URL de l'API
API_URL = "http://localhost:8000/predict"

# Liste des client_ids disponibles (dummy)
CLIENT_IDS = [
    "100001", "100002", "100003", "100004", "100005",
    "100006", "100007", "100008", "100009", "100010"
]

def simulate_requests(num_requests: int = 100):
    """
    Simule des requêtes à l'API
    
    Args:
        num_requests: Nombre de requêtes à simuler
    """
    print(f"🚀 Simulation de {num_requests} requêtes à l'API...")
    print(f"📍 URL : {API_URL}")
    print("-" * 50)
    
    success_count = 0
    error_count = 0
    
    for i in range(num_requests):
        # Choisir un client_id aléatoire
        client_id = random.choice(CLIENT_IDS)
        
        try:
            # Appeler l'API
            response = requests.get(f"{API_URL}/{client_id}")
            
            if response.status_code == 200:
                data = response.json()
                success_count += 1
                print(f"✅ [{i+1}/{num_requests}] Client {client_id} | "
                      f"Score: {data['score']} | {data['decision']}")
            else:
                error_count += 1
                print(f"❌ [{i+1}/{num_requests}] Erreur {response.status_code}")
        
        except Exception as e:
            error_count += 1
            print(f"❌ [{i+1}/{num_requests}] Exception: {e}")
        
        # Pause aléatoire entre 0.1 et 0.5 secondes (réaliste)
        time.sleep(random.uniform(0.1, 0.5))
    
    print("-" * 50)
    print(f"✅ Succès : {success_count}/{num_requests}")
    print(f"❌ Erreurs : {error_count}/{num_requests}")
    print(f"📊 Logs enregistrés dans : data/prod/logs_production.csv")

if __name__ == "__main__":
    simulate_requests(100)