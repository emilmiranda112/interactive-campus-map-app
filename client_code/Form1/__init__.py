from ._anvil_designer import Form1Template
import anvil.server
from anvil import *

class Form1(Form1Template):
  def __init__(self, **properties):
    # Set up components and initialize form
    self.init_components(**properties)

    # 1. Apply your custom "Disney/Themed" style to the map face
    # Paste your Snazzy Maps JSON inside the brackets below
    custom_map_style = [
      {
        "featureType": "landscape",
        "elementType": "geometry.fill",
        "stylers": [
          {
            "color": "#fcfcfc"
          }
        ]
      },
      {
        "featureType": "poi",
        "elementType": "labels",
        "stylers": [
          {
            "color": "#8b8484"
          },
          {
            "visibility": "off"
          }
        ]
      },
      {
        "featureType": "poi.business",
        "elementType": "labels",
        "stylers": [
          {
            "visibility": "off"
          }
        ]
      },
      {
        "featureType": "road",
        "elementType": "geometry.fill",
        "stylers": [
          {
            "color": "#c7b8b8"
          }
        ]
      },
      {
        "featureType": "water",
        "elementType": "geometry.fill",
        "stylers": [
          {
            "color": "#3c3939"
          }
        ]
      }
    ]
    self.map_campus.map_type_id = 'satellite'

    # 2. Call the server module backend you wrote on Day 6 to get data
    self.locations = anvil.server.call('load_campus_data')
    
    # 3. Center the map automatically near your campus coordinates
    # (Update these two numbers to match your actual campus center!)
    if self.locations:
      self.map_campus.center = anvil.GoogleMap.LatLng(33.163395832473206, -117.24753965466618)
      self.map_campus.zoom = 16

      # 4. Generate the markers dynamically onto your custom map face
      self.drop_map_markers()

  def drop_map_markers(self):
    # Loop through your parsed CSV data to drop pins
    for loc in self.locations:
      marker = anvil.GoogleMap.Marker(
        position=anvil.GoogleMap.LatLng(loc['lat'], loc['lng']),
        title=loc['name']
      )

      # Tag the marker object with its description for later UI popups
      marker.tag = loc['desc']

      # Add the marker to your styled map canvas
      self.map_campus.add_component(marker)

  @handle("dropdown_locations", "change")
  def dropdown_locations_change(self, **event_args):
    """This method is called when the text in this text box is edited"""
    pass  # Wr
