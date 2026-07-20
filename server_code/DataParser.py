import anvil.server
import csv
import io

# This decorator makes the function callable from your frontend UI forms!
@anvil.server.callable
def load_campus_data():
  # 1. We load the CSV file that you saved in your repository
  # (Anvil allows us to access repository assets directly)
  try:
    with open("theme/assets/campus_locations.csv", "r") as f:
      csv_data = f.read()
  except FileNotFoundError:
    # Fallback dataset in case the file sync is still processing
    return [
      {"name": "Main Library", "lat": 37.77492, "lng": -122.41941, "desc": "The quietest study spot on campus."},
      {"name": "Student Center", "lat": 37.77520, "lng": -122.41890, "desc": "The hub for student clubs and food."}
    ]

  # 2. Parse the CSV text using Python's built-in CSV module
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
