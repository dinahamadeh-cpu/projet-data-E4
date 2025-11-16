from data.get_data import ensure_cleaned_data, check_raw_data
from src.app import create_app 
from src.utils.lecture_BDD import lecture_BDD_histo 

def main():
    print(" === Démarrage du Dashboard d'Analyse des Pathologies ===\n")
    
    print(" 1. Vérification des données brutes...")
    raw_ok = check_raw_data()

    if raw_ok:
        print("\n 2. Vérification / génération des données nettoyées...")
        data_ok = ensure_cleaned_data() 
        
        if data_ok:
            print("\n 3. Chargement du DataFrame depuis la BDD...")
            try:
                df = lecture_BDD_histo()
            except FileNotFoundError as e:
                print(f" Erreur critique : {e}. Le fichier de BDD devrait exister à ce stade.")
                return
            except Exception as e:
                print(f" Erreur lors du chargement du DataFrame : {e}")
                return

            print("\n 4. Lancement du serveur Dash...")
            try:
                app = create_app(df) 
                
                port_number = 8050 
                print(f"🌍 Dashboard disponible à l'adresse : http://127.0.0.1:{port_number}/")
                app.run(debug=True, port=port_number) 
                
            except Exception as e:
                print(f" Erreur lors du lancement du serveur Dash : {e}")
        else:
            print("\n Impossible de lancer l'application : La base de données nettoyée n'a pu être créée ou est vide.")
            
    else:
        print("\n Impossible de poursuivre : données brutes manquantes. Veuillez placer le fichier ZIP dans le dossier rawdata.")

if __name__ == "__main__":
    main()