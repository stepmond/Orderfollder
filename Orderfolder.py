import chardet
import ctypes
import datetime
import hashlib
import logging
import os
import psutil
import shutil
import time
from config import ROOT_FOLDER, PARENT_FOLDER, FILE_ORDERED_FOLDER, ORGANIZE_BY_DATE, OPERATION_MODE, FILE_CATEGORIES, prepare_path_for_long_names, compiled_file_exclusion_patterns, compiled_folder_exclusion_patterns

# Lancement de la vérification du disque
# drive_letter = os.path.splitdrive(ROOT_FOLDER)[0]
# check_disk_partition(drive_letter)




# Variables globales
# Lors de la configuration des dossiers
# ROOT_FOLDER = prepare_path_for_long_names(r"G:\HUMBERT\archive\G\CLIENTS\HUMBERTFabBackup\2023-04-18\DESKTOP-6L0320C\user\archive")
# parent_folder = os.path.dirname(ROOT_FOLDER)  # Remonter d'un niveau dans la hiérarchie des dossiers
# file_ordered_folder = prepare_path_for_long_names(os.path.join(parent_folder, "Files Ordered"))

# organize_by_date = False  # Mettre à True pour organiser les fichiers dans des sous-dossiers datés
# operation_mode = "copy"  # Choisir "move" pour déplacer les fichiers, "copy" pour les copier

# Configuration du fichier log, recréation après relance du script (filemode w au lieu de filemode a)
log_file = os.path.join(PARENT_FOLDER, "file_ordered_log.txt")
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M', filemode='w')

logging.info("Début de l'organisation des fichiers")


def get_folder_size(folder):
    """Retourne la taille totale en octets du dossier spécifié."""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                total_size += os.path.getsize(fp)
            except FileNotFoundError:
                # Si un fichier est introuvable (par exemple, s'il a été supprimé pendant la course du script)
                continue
            except PermissionError:
                # Si un fichier est verrouillé ou que l'accès est refusé
                continue
    return total_size
    
    
def format_size(size_in_bytes):
    """Formatte la taille en Mo avec des séparateurs de milliers."""
    size_in_mb = size_in_bytes / (1024 * 1024)
    return f"{size_in_mb:,.0f}".replace(",", " ")

# Calculer la taille du dossier source
source_folder_size = get_folder_size(ROOT_FOLDER)

# Formater et afficher la taille du dossier source
formatted_size_source = format_size(source_folder_size)
        
    
def categorize_file(extension):
    """Catégorise les fichiers en fonction de leur extension"""
    for category, extensions in FILE_CATEGORIES.items():
        if extension in extensions:
            return category
    return "Divers"
    
    
def hash_file(file_path):
    """Calcule le hash BLAKE2b d'un fichier"""
    hash_alg = hashlib.blake2b()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_alg.update(chunk)
        return hash_alg.hexdigest()
        
    except (PermissionError, FileNotFoundError, IOError) as e:
        logging.error(f"Erreur avec le fichier {file_path}: {e}")
        print(f"Erreur : {e}")
        return None
    
    
def is_excluded(file_or_folder):
    """Vérifie si un fichier ou dossier est exclu en utilisant des regex (insensible à la casse)."""
    file_or_folder = file_or_folder.lower()
    patterns = compiled_folder_exclusion_patterns if os.path.isdir(file_or_folder) else compiled_file_exclusion_patterns
    return any(pattern.match(os.path.basename(file_or_folder)) for pattern in patterns)

    
def organize_files(organize_by_date=ORGANIZE_BY_DATE, operation_mode=OPERATION_MODE):
    """Organise les fichiers selon les catégories définies, avec vérification d'intégrité et déduplication"""
    if not os.path.exists(FILE_ORDERED_FOLDER):
        os.makedirs(FILE_ORDERED_FOLDER)
        
    hash_dict = {}
    
    total_start_time = time.time()  # Temps de début global

    for subdir, dirs, files in os.walk(ROOT_FOLDER):
        subdir = prepare_path_for_long_names(subdir)  # Appliquer à subdir
        for file in files:
            file_path = prepare_path_for_long_names(os.path.join(subdir, file))
            if is_excluded(file_path):
                logging.info(f"Fichier exclu: {file_path}")
                continue
                
            try:
                # Temps de début pour chaque fichier
                start_time = time.time()
                
                file_size = os.path.getsize(file_path)
                file_mtime = os.path.getmtime(file_path)
                logging.info(f"Traitement du fichier : {file_path} (taille : {file_size / (1024*1024):.2f} Mo)")
                print(f"Traitement du fichier : {file_path} (taille : {file_size / (1024*1024):.2f} Mo)")

                # Hashage du fichier source
                file_hash = hash_file(file_path)
                if file_hash is None:
                    logging.warning(f"Le hash du fichier {file_path} n'a pas pu être calculé. Fichier ignoré.")
                    continue
                
                # Vérification de déduplication
                if file_hash in hash_dict:
                    logging.info(f"Fichier dupliqué détecté et ignoré: {file_path}")
                    continue

                file_category = categorize_file(file.split('.')[-1].lower())
                target_folder = prepare_path_for_long_names(os.path.join(FILE_ORDERED_FOLDER, file_category))
                
                if organize_by_date:
                    date_str = datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d')
                    target_folder = os.path.join(target_folder, date_str)

                if not os.path.exists(target_folder):
                    os.makedirs(target_folder)

                target_file = prepare_path_for_long_names(os.path.join(target_folder, file))
                
                if os.path.exists(target_file):
                    target_size = os.path.getsize(target_file)
                    target_mtime = os.path.getmtime(target_file)
                    
                    # Comparaison par taille et date de modification
                    if file_size == target_size and file_mtime == target_mtime:
                        logging.info(f"Le fichier {file_path} est déjà présent et complet dans le dossier cible.")
                        print(f"Le fichier {file_path} est déjà présent et complet dans le dossier cible.")
                        continue
                    else:
                        logging.warning(f"Le fichier {target_file} pourrait être incomplet ou corrompu. Remplacement par une version correcte.")

                # Copier ou déplacer le fichier après vérification
                if operation_mode == "move":
                    shutil.move(file_path, target_file)
                    logging.info(f"Fichier déplacé: {file_path} -> {target_folder}")
                elif operation_mode == "copy":
                    shutil.copy2(file_path, target_file)
                    logging.info(f"Fichier copié: {file_path} -> {target_folder}")

                # Enregistrer le hash dans le dictionnaire pour déduplication future
                hash_dict[file_hash] = target_file
                
                # Fin du traitement du fichier
                elapsed_time = time.time() - start_time
                logging.info(f"Traitement terminé pour : {elapsed_time:.0f} secondes : {file_path}")
                print(f"Traitement terminé pour : {file_path} (temps : {elapsed_time:.0f} secondes)")

            except (PermissionError, FileNotFoundError, IOError) as e:
                logging.error(f"Erreur avec le fichier {file_path}: {e}")
                print(f"Erreur avec le fichier : {e}")

    total_elapsed_time = time.time() - total_start_time  # Fin du calcul du temps de traitement réel
    formatted_total_time = time.strftime("%H:%M:%S", time.gmtime(total_elapsed_time))
    logging.info(f"Temps total de traitement réel : {formatted_total_time}")
    print(f"Temps total de traitement réel : {formatted_total_time}") 
    
    # Calcul de la taille du dossier traité
    final_size_in_bytes = get_folder_size(FILE_ORDERED_FOLDER)
    final_size_in_mb = round(final_size_in_bytes / (1024 * 1024))  # Taille en Mo, arrondie sans virgule
    print(f"Taille du dossier trié : {final_size_in_mb} Mo")
    logging.info(f"Taille du dossier trié : {final_size_in_mb} Mo")    
    
    return formatted_total_time, final_size_in_bytes
    
    
logging.info("Organisation des fichiers terminée")                


# Organisation des fichiers
if __name__ == "__main__":
    # Organisation des fichiers
    formatted_total_time, final_size_in_mb = organize_files()
    print("Tri des fichiers terminé.")