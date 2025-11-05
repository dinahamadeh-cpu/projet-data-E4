# import os
# import requests


# def fetch_data(
#     url: str = "https://www.data.gouv.fr/api/1/datasets/r/5f71ba43-afc8-43a0-b306-dafe29940f9c",
#     output_path: str = "data/rawdata/"
# ) -> None:

    
#     os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
#     headers = {"User-Agent": "Mozilla/5.0 (compatible; DataProjectBot/1.0)"}
    
#     print(f"Téléchargement des données depuis : {url}")
#     try:
#         with requests.get(url, headers=headers, stream=True, timeout=30) as response:
#             response.raise_for_status()
#             with open(output_path, "wb") as f:
#                 for chunk in response.iter_content(chunk_size=8192):
#                     if chunk:
#                         f.write(chunk)
#         print(f" Données enregistrées dans : {output_path}")
#     except requests.exceptions.RequestException as e:
#         print(f"Erreur lors du téléchargement : {e}")


# if __name__ == "__main__":
#     fetch_data()

import os
import requests
import subprocess

def fetch_data(
    url: str = "https://www.data.gouv.fr/api/1/datasets/r/5f71ba43-afc8-43a0-b306-dafe29940f9c",
    output_path: str = "data/rawdata/"
) -> None:
    """
    Télécharge les données brutes depuis data.gouv.fr
    (ne télécharge que si le fichier n'existe pas déjà)
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if os.path.exists(output_path):
        print(f" Données déjà téléchargées : {output_path}")
        return

    headers = {"User-Agent": "Mozilla/5.0 (compatible; DataProjectBot/1.0)"}

    print(f"Téléchargement des données depuis : {url}")
    try:
        with requests.get(url, headers=headers, stream=True, timeout=60) as response:
            response.raise_for_status()
            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        print(f" Données enregistrées dans : {output_path}")
    except requests.exceptions.RequestException as e:
        print(f" Erreur lors du téléchargement : {e}")


def check_and_clean_data(
    cleaned_db_path: str = "data/cleaned/data_patologies_cleaned.db",
    cleaning_script_path: str = "data/clean_data.py"
) -> None:
    """
    Vérifie si la base de données nettoyée (.db) existe déjà.
    Si non, exécute automatiquement le script de nettoyage.
    """
    os.makedirs(os.path.dirname(cleaned_db_path), exist_ok=True)

    if os.path.exists(cleaned_db_path):
        print(f" Base de données nettoyée déjà présente : {cleaned_db_path}")
    else:
        print(" Base nettoyée introuvable. Lancement du nettoyage...")
        try:
            result = subprocess.run(
                ["python", cleaning_script_path],
                check=True,
                capture_output=True,
                text=True
            )
            print(" Nettoyage terminé avec succès.")
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(" Erreur lors de l'exécution du script de nettoyage :")
            print(e.stderr)

    # Vérification basique du fichier .db
    if os.path.exists(cleaned_db_path):
        size_mb = os.path.getsize(cleaned_db_path) / (1024 * 1024)
        if size_mb < 1:
            print(f" Attention : la base semble vide ({size_mb:.2f} Mo). Vérifie ton script de nettoyage.")
        else:
            print(f" Taille de la base nettoyée : {size_mb:.2f} Mo")
    else:
        print(" Le fichier .db n’a pas été créé correctement.")


if __name__ == "__main__":
    # Étape 1 : Télécharger les données brutes
    fetch_data()

    # Étape 2 : Vérifier / générer la base nettoyée
    check_and_clean_data()
