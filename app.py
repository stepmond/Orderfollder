import streamlit as st
import os
from config import ROOT_FOLDER, FILE_ORDERED_FOLDER, ORGANIZE_BY_DATE, OPERATION_MODE

from Orderfolder import  format_size, source_folder_size, formatted_size_source, organize_files 
from pathlib import Path


# Initialiser l'état du bouton
if 'button_disabled' not in st.session_state:
    st.session_state.button_disabled = False


# Fonction pour nettoyer les chemins
def clean_path(path):
    """Supprime le préfixe '\\\\?\\' d'un chemin si présent."""
    if path.startswith('\\\\?\\'):
        return path[4:]
    return path


# Nettoyer les chemins pour l'affichage
cleaned_root_folder = clean_path(ROOT_FOLDER)
cleaned_file_ordered_folder = clean_path(FILE_ORDERED_FOLDER)

# Calcul du temps approximatif de traitement en minutes
# 1 Go (1024 Mo) est traité en 1 minute, donc on divise par 1000
approx_time_minutes = round(source_folder_size / (1024 * 1024 * 1000),2) 

# Si le temps est inférieur à 1 minute, l'afficher en secondes pour plus de précision.
if approx_time_minutes < 1:
    approx_time_seconds = round(approx_time_minutes * 60)  # Convertir en secondes
    approx_time_text = f"{approx_time_seconds} secondes"
else:
    approx_time_text = f"{approx_time_minutes} minutes"


# Titre de l'application
st.title(f"Organisation et dédoublonnage du dossier '{os.path.basename(cleaned_root_folder)}'")

# Affichage des variables pour les dossiers
st.info(f"Les fichiers du dossier à traiter seront triés et dédoublonnés selon leurs extensions dans des sous-dossiers  du dossier de destination, organisés selon les types de fichier\n(Dossiers Images, Vidéos, Exécutables, Documents, Musiques, Compressés, Divers.\n\nLe dossier de destination se trouve au même niveau que le dossier à traiter, et s'appel Files Ordered.")


# Ajouter une option pour choisir le dossier à traiter
st.write(f"Dossier à traiter : {cleaned_root_folder}")


# Afficher le dossier choisi
cleaned_destination_folder = clean_path(os.path.dirname(ROOT_FOLDER))
st.write(f"Dossier de destination : {cleaned_destination_folder}\Files Ordered")


# Créer deux colonnes pour les options d'organisation et de mode de traitement
col1, col2 = st.columns(2)

# Choisir l'organisation par date ou pas
with col1:
    organize_by_date = st.checkbox("Organiser par date", value=ORGANIZE_BY_DATE)

# Choisir entre copier ou déplacer les fichiers
with col2:
    operation_mode = st.radio("Mode de traitement", options=["Copier", "Déplacer"])

# Conversion du mode de traitement en chaîne compatible
operation_mode = "copy" if operation_mode == "Copier" else "move"

st.write(f"Taille du dossier à traiter : {formatted_size_source} Mo")
st.write(f"Temps approximatif de traitement : {approx_time_text} (1GO par Mn environ).")

# Bouton pour exécuter le script
if st.button("Lancer le traitement", disabled=st.session_state.button_disabled):
    # Désactiver le bouton pour éviter de cliquer pendant le traitement
    st.session_state.button_disabled = True

    # Afficher un message indiquant que le traitement est en cours
    with st.spinner('Traitement en cours...\nLes fichiers lourds en traitement peuvent faire penser que le script a planté, vérifier dans le prompt'):
        # Lancer le script principal uniquement si le bouton est pressé
        formatted_total_time, final_size_in_mb = organize_files(organize_by_date, operation_mode)
        
    # Afficher l'estimation du temps de traitement
    # st.write(f"Estimation du temps total de traitement : {estimated_time}")
    
    # Appliquer format_size pour un affichage intuitif
    formatted_final_size = format_size(final_size_in_mb)  # Convertir en octets avant formatage
 
    # Réactiver le bouton après la fin du traitement
    st.session_state.button_disabled = False
    st.success("Le tri et le dédoublonnage des fichiers sont terminés.")
    st.write(f"Temps réel de traitement : {formatted_total_time}")
    st.write(f"Taille finale du dossier trié et dédoublonné : {formatted_final_size} Mo")
