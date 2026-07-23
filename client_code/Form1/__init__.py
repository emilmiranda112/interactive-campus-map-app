from ._anvil_designer import Form1Template
import anvil.server
from anvil import *
import anvil.js

class Form1(Form1Template):
  def __init__(self, **properties):
    # Set up components and initialize form
    self.init_components(**properties)
    
    self.user_marker = None
    self.location_checkboxes = {}
    

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

    # 4. Populate Main Category Dropdown dynamically
    categories = sorted(list(set(loc.get('category', '').strip() for loc in self.locations if loc.get('category'))))
    self.drop_down_category.items = [("Select a category...", None)] + [(cat, cat) for cat in categories]


    def start_user_tracking(self):
      """Requests GPS permission and tracks the user's position live."""
    geolocation = anvil.js.window.navigator.geolocation

    if geolocation:
      options = {
        'enableHighAccuracy': True,
        'maximumAge': 0,
        'timeout': 10000
      }
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
        icon="https://maps.google.com/mapfiles/ms/icons/blue-dot.png"
      )
      self.map_campus.add_component(self.user_marker)
    else:
      # Just update the existing marker's position
      self.user_marker.position = user_pos

  def handle_location_error(self, error, **event_args):
    """Handles GPS permission denial or timeouts gracefully."""
    print("Could not retrieve user location:", error.message)
    # 5. Draw initial map state & start GPS tracking
    self.drop_map_markers()
    self.start_user_tracking()

  @handle("drop_down_category", "change")
  def drop_down_category_change(self, **event_args):
    """This method is called when an item is selected"""
    """Triggered when user selects a category (e.g. Restrooms, Sports)"""
    selected_cat = self.drop_down_category.selected_value

    # Clear out previous sub-checkboxes
    self.panel_sub_checkboxes.clear()
    self.location_checkboxes = {}

    if not selected_cat:
      self.drop_map_markers()
      return

    for idx, loc in enumerate(self.locations):
      if loc.get('category', '').strip() == selected_cat:
        chk = anvil.CheckBox(text=loc['name'], checked=True)
        chk.set_event_handler('change', self.individual_checkbox_change)

        # Save reference using unique index `idx` as key
        self.location_checkboxes[idx] = {'checkbox': chk, 'location': loc}
        self.panel_sub_checkboxes.add_component(chk)

    self.drop_map_markers()

  def individual_checkbox_change(self, **event_args):
    """Triggered whenever any sub-checkbox is checked or unchecked"""
    self.drop_map_markers()

  def drop_map_markers(self):
    # Clear canvas
    self.map_campus.clear()

    # Re-add live GPS location pin if active
    if getattr(self, 'user_marker', None) is not None:
      self.map_campus.add_component(self.user_marker)

    # Define icon styles & sizes
    icon_size = anvil.GoogleMap.Size(35, 30)
    category_icons = {
      "Restrooms": {
        'url': "_/theme/BlueRestroomIcon.png",
        'scaledSize': icon_size
      },
      "Sports": {
        'url': "_/theme/RunningIcon.png",
        'scaledSize': anvil.GoogleMap.Size(50, 50)
      },
      "Classrooms": {
        'url': "_/theme/ClassroomIcon.png",
        'scaledSize': icon_size
      },
      "Academic & Culture": {
        'url': "_/theme/BookIcon.png",
        'scaledSize': icon_size
      }
    }

    # Only draw markers whose specific sub-checkbox IS checked!
    for key, item in self.location_checkboxes.items():
      if item['checkbox'].checked:
        loc = item['location']
        category = loc.get('category', '').strip()
        chosen_icon = category_icons.get(category, "http://maps.google.com/mapfiles/ms/icons/red-dot.png")

        marker = anvil.GoogleMap.Marker(
          position=anvil.GoogleMap.LatLng(loc['lat'], loc['lng']),
          title=loc['name'],
          icon=chosen_icon
        )
        marker.tag = loc['desc']
        marker.add_event_handler("click", self.marker_click)
        self.map_campus.add_component(marker)

  def marker_click(self, sender, **event_args):
    """Fires when a marker pin is clicked"""
    alert(content=sender.tag, title=sender.title)

