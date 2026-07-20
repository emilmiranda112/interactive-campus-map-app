import anvil.server
import csv
import io

@anvil.server.callable
def load_campus_data():
  # Since it's right in the same folder now, we can open it directly!
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