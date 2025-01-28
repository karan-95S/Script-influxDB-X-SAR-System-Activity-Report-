#!/bin/bash

# Récupération de la date du jour précédent
DATE=$(date -d "$year-$month-$day - 1 day" +"%Y-%m-%d")
year=$(date +"%Y")
month=$(date +"%m")
day=$(date +"%d")

# Affichage des informations
echo "Date actuelle : $DATE"
echo "Année : $year"
echo "Mois : $month"
echo "Jour : $day"

# Chemin du fichier binaire (1er argument du script)
binary_file_path="$1/$year/$month"

# Vérification que le répertoire existe
if [ ! -d "$binary_file_path" ]; then
    echo "Erreur : Le chemin spécifié n'existe pas -> $binary_file_path"
    exit 1
fi

# Fichier source SAR
binary_file="$binary_file_path/sar-$DATE"
if [ ! -f "$binary_file" ]; then
    echo "Erreur : Le fichier source n'existe pas -> $binary_file"
    exit 1
fi

# Génération du fichier CSV
csv_file="$binary_file_path/sar-$DATE.csv"
sudo sadf -d -T "$binary_file" -- -u > "$csv_file"

sed -i 's/,/./g' "$csv_file"
# Vérification de la création du fichier CSV
if [ -f "$csv_file" ]; then
    echo "Fichier CSV créé avec succès : $csv_file"
    echo "Contenu du fichier CSV :"
    cat "$csv_file"
else
    echo "Erreur : Échec de la création du fichier CSV"
    exit 1
fi

python3 script_data_influx.py "$1" "$csv_file"
