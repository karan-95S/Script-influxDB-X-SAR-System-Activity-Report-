import csv
import os
from datetime import datetime
import string
import sys
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# Configuration InfluxDB
influx_url = "http://localhost:8086"
token = os.environ.get("INFLUXDB_TOKEN")
org = "GCU asso"
bucket = "verif"
csv_file = sys.argv[1]

# Connexion à InfluxDB
client = InfluxDBClient(url=influx_url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)

# Fonction pour nettoyer les nombres avec des virgules
def clean_decimal(value):
    return float(value.replace(",", "."))

# Lecture et importation des données CSV
with open(csv_file, "r") as file:
    sample = file.read(1024)
    delimiter = "," if "," in sample else ";"  # Détecter automatiquement le délimiteur
    file.seek(0)
    csv_reader = csv.reader(file, delimiter=delimiter)
    
    # Corriger les en-têtes si nécessaire
    headers = next(csv_reader)
    print(f"En-têtes détectés : {headers}\n")

    # Si les en-têtes sont incorrects, les remplacer par les bons
    correct_headers = ["# hostname", "interval", "timestamp", "CPU", "%user", "%nice", "%system", "%iowait", "%steal", "%idle"]
    if headers[0] != "# hostname":  # Vérifie si les en-têtes sont incorrects
        print("Correction des en-têtes...")
        headers = correct_headers
    else:
        print("En-têtes corrects détectés.")

    # Utiliser les en-têtes corrigés pour le DictReader
    csv_reader = csv.DictReader(file, delimiter=delimiter, fieldnames=headers)
    points = []
    for row in csv_reader:
        print(f"Ligne lue : {row}\n")

        try:
            # Convertir le timestamp au format ISO pour InfluxDB
            timestamp_iso = datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S").isoformat()

            # Créer un point pour InfluxDB
            point = Point("cpu_usage") \
                .tag("hostname", row.get("# hostname", "unknown")) \
                .tag("CPU", row.get("CPU", "all")) \
                .field("user", clean_decimal(row["%user"])) \
                .field("nice", clean_decimal(row["%nice"])) \
                .field("system", clean_decimal(row["%system"])) \
                .field("iowait", clean_decimal(row["%iowait"])) \
                .field("steal", clean_decimal(row["%steal"])) \
                .field("idle", clean_decimal(row["%idle"])) \
                .time(timestamp_iso)
            points.append(point)
        except Exception as e:
            print(f"Erreur lors du traitement de la ligne : {e}, Ligne : {row}")

    if points:
        write_api.write(bucket=bucket, org=org, record=points)
        print(f"{len(points)} points insérés dans InfluxDB.")
    else:
        print("Aucun point valide n'a été généré.")

client.close()
print("Importation terminée.")
