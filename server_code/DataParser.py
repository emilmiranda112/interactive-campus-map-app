import anvil.server
import csv
import io
import urllib.request

@anvil.server.callable
def load_campus_data():
  # Insert your Raw GitHub URL here!
  github_csv_url = "https://raw.githubusercontent.com/emilmiranda112/interactive-campus-map-app/refs/heads/master/server_code/campus_locations.csv"

  # Fetch the latest CSV directly from GitHub
  req = urllib.request.Request(github_csv_url, headers={'User-Agent': 'Mozilla/5.0'})
  with urllib.request.urlopen(req) as response:
    csv_data = response.read().decode('utf-8')

  # Parse the CSV contents dynamically
  f_input = io.StringIO(csv_data)
  reader = csv.DictReader(f_input)

  parsed_locations = []
  for row in reader:
    parsed_locations.append({
      "name": row["name"],
      "lat": float(row["latitude"]),
      "lng": float(row["longitude"]),
      "desc": row["description"]
    })

  return parsed_locations