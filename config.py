import re
import os

def prepare_path_for_long_names(path):
    """Prépare un chemin pour gérer les noms de fichiers longs sous Windows."""
    if isinstance(path, str) and not path.startswith('\\\\?\\'):
        # Convertir en chemin long si le chemin n'est pas déjà préparé
        path = '\\\\?\\' + os.path.abspath(path)
    return path


ROOT_FOLDER = prepare_path_for_long_names(r"G:\LANDRIOT")
PARENT_FOLDER = os.path.dirname(ROOT_FOLDER)  # Remonter d'un niveau dans la hiérarchie des dossiers
FILE_ORDERED_FOLDER = prepare_path_for_long_names(os.path.join(PARENT_FOLDER, "Files Ordered"))

ORGANIZE_BY_DATE = False  # Mettre à True pour organiser les fichiers dans des sous-dossiers datés
OPERATION_MODE = "copy"  # Choisir "move" pour déplacer les fichiers, "copy" pour les copier


# Dictionnaire de catégories de la fonction categorize_file pour classer les fichiers récupérés par leur extension
FILE_CATEGORIES = {
    "Images": ['avif', 'bmp', 'esd', 'gif', 'jfif', 'jpg', 'jpeg', 'nef', 'pfi', 'png', 'psd', 'svg', 'tiff', 'tif', 'tnl', 'webp'],
    "Videos": ['3gp', 'avi', 'flv', 'mp4', 'mkv', 'mov', 'mxf', 'wma', 'wmv'],
    "Documents": ['asd', 'celtx', 'csv', 'doc', 'docm', 'docx', 'dotx', 'dotm', 'mdb', 'odt', 'ods', 'odp', 'odg', 'odf', 'ott', 'ots', 'otp', 'otg', 'one', 'oxps', 'potx', 'pps', 'ppt', 'pptx', 'pdf', 'rtf', 'skb', 'skp', 'thmx', 'txt', 'wps', 'xps', 'xls', 'xlsx', 'xlt'],
    "Music": ['aac', 'flac', 'm4a', 'mp3', 'ogg', 'wav'],
    "Programs": ['bat', 'exe', 'py', 'sh', 'apk'],
    "Compressed": ['7z', 'bz2', 'gz', 'iso', 'rar', 'tar', 'xz', 'zip'],
    "Divers": []  # Pour les extensions non spécifiées
}


# Liste des extensions à exclure, triées par ordre alphabétique
file_extensions_to_exclude = [
    'acl', 'apm', 'au', 'avastlic', 'bal', 'baf', 'bak', 'bin', 'bp', 'bpl', 'bt', 'cab', 'cache', 'cat', 
    'c32', 'cfg', 'chm', 'ch_', 'clg', 'cmd', 'com', 'conf', 'config', 'crash', 'crt', 'cue', 'css', 'cfx', 'crdownload',
    'dat', 'dah', 'dal', 'daw', 'db', 'dds', 'dic', 'dl_', 'dll', 'dmp', 'drv', 'dsi', 'eot', 'ex_', 'extra', 'final', 'fingerprint', 'fen', 'gdd', 'gbx', 
    'grle', 'hlp', 'htm', 'html', 'hpdata', 'i3d', 'icns', 'in_', 'inf', 'info', 'ini', 'inx', 'ico', 'itdb', 'itl', 'js', 'json', 'jsonlz4', 'key', 'ldb', 
    'log', 'man', 'map', 'mat', 'md5', 'mf', 'm3u', 'manifest', 'mof', 'mpf', 'mfl', 'msp', 'msi', 
    'mui', 'nib', 'nfo', 'nri', 'old', 'pac', 'part', 'pem', 'pbz', 'pcm', 'plist', 'pmp', 'pro', 'pzl', 'rdp', 'reg', 'rom', 'sai', 'sav', 'sdb', 'scr', 
    'scss', 'sdi', 'sharc', 'shapes', 'sii', 'srt', 'strings', 'swf', 'swp', 'swo', 'sys', 'sy_', 'thm', 'temp', 'tmp', 'tga', 
    'tobj', 'tpl', 'torrent', 'tre', 'ttf', 'ui', 'vdj', 'vdjsample', 'vdjsend', 'ver', 'vbs', 
    'wbcat', 'wim', 'woff', 'woff2', 'x', 'xib', 'xgf', 'xpi', 'xrm-ms', 'xml', 'ytf', 'yti'
]

# Génération automatique des motifs regex à partir des extensions
file_exclusion_patterns = [re.compile(rf'.*\.{ext}$', re.IGNORECASE) for ext in file_extensions_to_exclude]

# Ajout d'un motif pour les fichiers sans extension
file_exclusion_patterns.append(re.compile(r'^[^.]+$', re.IGNORECASE))

# Si vous avez des exclusions de dossiers spécifiques
folder_exclusion_patterns = [
    r'^excluded_folder$',  # Dossier spécifique à exclure
    # Ajoutez d'autres motifs ici
]

# Compile the regex patterns for better performance
compiled_file_exclusion_patterns = [pattern for pattern in file_exclusion_patterns]
compiled_folder_exclusion_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in folder_exclusion_patterns]