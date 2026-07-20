import anvil.server
import csv
import io

@anvil.server.callable
def load_campus_data():
  # Open the file exactly where Git places it in the root folder
  try:
    with open("campus_locations.csv", "r") as f:
      csv_data = f.read()
  except FileNotFoundError:
    # If there is a typo in the filename, look for lowercase version
    with open("campus_locations.csv", "r") as f:
      csv_data = f.read()

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