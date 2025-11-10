#import data.clean_data as clean_data
#import carte_departements as carte_departements
from src.hierarchiepatho import get_patho_hierarchy
from src.carte_departements import lecture_BDD, creation_carte_region
from src.dashboard import app
def main():
    #clean_data.main()
    #carte_departements.main()
    try:
        port_number = 8050
        print(f"🌍 Dashboard disponible à l'adresse : http://127.0.0.1:{port_number}/")
        app.run(debug=True, port=port_number)
        
    except Exception as e:
        print(f"❌ Erreur lors du lancement du serveur Dash : {e}")

if __name__ == "__main__":
    main()