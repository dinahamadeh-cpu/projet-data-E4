import os
import zipfile
import config
import data.clean_data as clean_data
import sqlite3
# --- Étape 1 : Vérification du ZIP et du CSV brut ---
def check_raw_data(zip_path: str = config.zip_file_name, csv_inside: str = config.csv_in_zip):
    """
    Vérifie la présence du fichier ZIP brut et du CSV à l'intérieur.
    """
    if not os.path.exists(zip_path):
        print(f" Le fichier brut est introuvable : {zip_path}")
        print(" Télécharge-le ou place-le dans le dossier data/rawdata/")
        return False

    try:
        with zipfile.ZipFile(zip_path, "r") as z:
            if csv_inside in z.namelist():
                print(f" Le fichier brut {csv_inside} est bien présent dans {zip_path}")
                return True
            else:
                print(f" Le fichier {csv_inside} n’a pas été trouvé dans le ZIP.")
                print(f"Contenu trouvé : {z.namelist()}")
                return False
    except zipfile.BadZipFile:
        print(f"Le fichier {zip_path} n’est pas un ZIP valide.")
        return False


# --- Étape 2 : Vérification ou génération du .db nettoyé ---
def ensure_cleaned_data(cleaned_db_path: str = config.db_name, table_name: str = config.table_name):
    """
    Vérifie si la base nettoyée (.db) existe et contient des données.
    Si non, exécute la fonction de nettoyage directement.
    """
    os.makedirs(os.path.dirname(cleaned_db_path), exist_ok=True)
    is_data_ready = False

    if os.path.exists(cleaned_db_path):
        try:
            con = sqlite3.connect(cleaned_db_path)
            # Vérifier si la table existe et si elle contient des lignes
            cursor = con.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            con.close()
            
            if row_count > 0:
                size_mb = os.path.getsize(cleaned_db_path) / (1024 * 1024)
                print(f" Base de données déjà prête ({size_mb:.2f} Mo, {row_count} lignes)")
                is_data_ready = True
            else:
                print(" Base trouvée mais ne contient pas de données ou la table est vide. Relancement du nettoyage...")
        except sqlite3.OperationalError:
            print(" Base trouvée mais illisible ou table manquante. Relancement du nettoyage...")
        except Exception as e:
            print(f" Erreur inattendue lors de la vérification de la base : {e}. Relancement du nettoyage...")

    if not is_data_ready:
        print(" Base nettoyée introuvable ou vide. Lancement du nettoyage...")
        try:
            # Exécuter directement la fonction de nettoyage
            clean_data.run_cleaning_process()
            # Revérifier après le nettoyage
            if os.path.exists(cleaned_db_path):
                con = sqlite3.connect(cleaned_db_path)
                cursor = con.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]
                con.close()
                if row_count > 0:
                     print("Nettoyage terminé avec succès et base remplie.")
                     is_data_ready = True
                else:
                    print("Attention : Le nettoyage s'est exécuté, mais la base reste vide.")
            else:
                print("Erreur : Le script de nettoyage n'a pas créé le fichier de base de données.")
        except Exception as e:
            print(f" Erreur lors de l’exécution du script de nettoyage : {e}")
            is_data_ready = False

    return is_data_ready
