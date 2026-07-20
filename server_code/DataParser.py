import anvil.server
import csv
import io

@anvil.server.callable
def load_campus_data():
  # We place your exact CSV text inside a Python multi-line string block!
  csv_data = """name,latitude,longitude,description
Longhorn Stadium,33.16778653811,-117.24888490044398,Where our track and field events take place
Longhorn Baseball Field,33.16767357499181,-117.2471256499127,Where our baseball games take place
Varsity Softball Field,33.167470321828444,-117.24682116818746,Where our softball games take place
Performing Arts Center,33.16759231243326,-117.24619196969348,Where our plays take place
Gymnasium,33.16928622384654,-117.2458165100435,Where our basketball games take place
Library,33.16923944548034,-117.24784133852441,The quietest place to study
"""

  # This treats the string exactly like an open file on your computer
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