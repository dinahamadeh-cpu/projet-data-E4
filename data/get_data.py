import os
import zipfile
import subprocess
import config

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
def check_cleaned_data(cleaned_db_path: str = config.db_name, cleaning_script_path: str = "data/src/clean_data.py"):
    """
    Vérifie si la base nettoyée (.db) existe et est non vide.
    Si non, exécute automatiquement le script de nettoyage.
    """
    os.makedirs(os.path.dirname(cleaned_db_path), exist_ok=True)

    if os.path.exists(cleaned_db_path):
        size_mb = os.path.getsize(cleaned_db_path) / (1024 * 1024)
        if size_mb > 1:
            print(f" Base de données déjà prête ({size_mb:.2f} Mo)")
            return True
        else:
            print(f"  Base trouvée mais semble vide ({size_mb:.2f} Mo). Relancement du nettoyage...")
    else:
        print(" Base nettoyée introuvable. Lancement du nettoyage...")

    # Si la base est absente ou vide → lancer le nettoyage
    try:
        subprocess.run(["python", cleaning_script_path], check=True)
        print("Nettoyage terminé avec succès.")
    except subprocess.CalledProcessError as e:
        print(f" Erreur lors de l’exécution du script de nettoyage : {e}")
        return False

    return os.path.exists(cleaned_db_path)


if __name__ == "__main__":
    print(" Vérification des données brutes...")
    raw_ok = check_raw_data()

    if raw_ok:
        print("\n Vérification / génération des données nettoyées...")
        check_cleaned_data()
    else:
        print(" Impossible de poursuivre : données brutes manquantes.")


