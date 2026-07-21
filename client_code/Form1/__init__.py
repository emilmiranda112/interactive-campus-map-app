from ._anvil_designer import Form1Template
import anvil.server
from anvil import *
import anvil.js

class Form1(Form1Template):
  def __init__(self, **properties):
    self.user_marker = None
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
    # 2. Keep map centered on your specific hardcoded location
    self.map_campus.center = anvil.GoogleMap.LatLng(33.163395832473206, -117.24753965466618)
    self.map_campus.zoom = 17
    
    self.active_categories = set()
    # 3. Fetch dataset from DataParser backend
    self.locations = anvil.server.call('load_campus_data')

    # 4. Generate initial markers
    self.drop_map_markers()
    self.start_user_tracking()

  def start_user_tracking(self):
    """Requests GPS permission and tracks the user's position live."""
    geolocation = anvil.js.window.navigator.geolocation

    if geolocation:
      # Options for high accuracy live GPS tracking
      options = {
        'enableHighAccuracy': True,
        'maximumAge': 0,
        'timeout': 10000
      }

      # watchPosition updates automatically whenever the user moves!
      geolocation.watchPosition(
        self.update_user_location,
        self.handle_location_error,
        options
      )
    else:
      print("Geolocation is not supported by this browser.")

  def update_user_location(self, position, **event_args):
    """Callback function triggered every time the user's coordinates change."""
    lat = position.coords.latitude
    lng = position.coords.longitude
    user_pos = anvil.GoogleMap.LatLng(lat, lng)

    # If user marker doesn't exist yet, create it
    if self.user_marker is None:
      self.user_marker = anvil.GoogleMap.Marker(
        position=user_pos,
        title="You are here!",
        icon="https://maps.google.com/mapfiles/ms/icons/blue-dot.png"  # Distinct blue pin
      )
      self.map_campus.add_component(self.user_marker)
    else:
      # Just update the existing marker's position
      self.user_marker.position = user_pos

  def handle_location_error(self, error, **event_args):
    print("Could not retrieve user location:", error.message)
  def drop_map_markers(self):
    # Clear existing map markers
    self.map_campus.clear()

    #Re-add user live location
    if getattr(self, 'user_marker', None) is not None:
      self.map_campus.add_component(self.user_marker)
      
    active_categories = []
    # Check states of your checkboxes
    if self.check_box_academic.checked:
      active_categories.append("Academic & Culture")
    if self.check_box_sports.checked:
      active_categories.append("Sports")
    if self.check_box_restrooms.checked:
      active_categories.append("Restrooms")
    if self.check_box_classrooms.checked:
      active_categories.append("Classrooms")

    # Add markers that match selected categories
    for loc in self.locations:
      category = loc.get('category', '').strip()
      if category in active_categories:
        marker = anvil.GoogleMap.Marker(
          position=anvil.GoogleMap.LatLng(loc['lat'], loc['lng']),
          title=loc['name']
        )
        marker.tag = loc['desc']
        self.map_campus.add_component(marker)

  @handle("check_box_sports", "change")
  def check_box_sports_change(self, **event_args):
    """This method is called when this checkbox is checked or unchecked"""
    self.drop_map_markers()

  @handle("check_box_academic", "change")
  def check_box_academics_change(self, **event_args):
    """This method is called when this checkbox is checked or unchecked"""
    self.drop_map_markers()

  @handle("check_box_restrooms", "change")
  def check_box_restrooms_change(self, **event_args):
    """This method is called when this checkbox is checked or unchecked"""
    self.drop_map_markers()

  @handle("check_box_classrooms", "change")
  def check_box_classrooms_change(self, **event_args):
    """This method is called when this checkbox is checked or unchecked"""
    self.drop_map_markers()

