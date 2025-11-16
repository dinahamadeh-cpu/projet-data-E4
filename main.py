from data.get_data import ensure_cleaned_data, check_raw_data
from src.app import app
import config # Ajout de l'import pour accéder au port si nécessaire

def main():
    print(" === Démarrage du Dashboard d'Analyse des Pathologies ===\n")
    
    print(" 1. Vérification des données brutes...")
    raw_ok = check_raw_data()

    if raw_ok:
        print("\n 2. Vérification / génération des données nettoyées...")
        # L'appel à ensure_cleaned_data lance le nettoyage si la BDD est absente ou vide.
        data_ok = ensure_cleaned_data() 
        
        if data_ok:
            print("\n 3. Lancement du serveur Dash...")
            try:
                # Utiliser le port 8050, ou le port défini dans config si vous en avez un
                port_number = 8050 
                print(f" Dashboard disponible à l'adresse : http://127.0.0.1:{port_number}/")
                # Attention : Pour une utilisation en production, retirez debug=True.
                app.run(debug=True, port=port_number) 
                
            except Exception as e:
                print(f" Erreur lors du lancement du serveur Dash : {e}")
        else:
            print("\n Impossible de lancer l'application : La base de données nettoyée n'a pu être créée ou est vide.")
            
    else:
        print("\n Impossible de poursuivre : données brutes manquantes. Veuillez placer le fichier ZIP dans le dossier rawdata.")

if __name__ == "__main__":
    main()