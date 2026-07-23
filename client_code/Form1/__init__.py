from ._anvil_designer import Form1Template
import anvil.server
from anvil import *
import anvil.js

class Form1(Form1Template):
  def __init__(self, **properties):
    # Set up components and initialize form
    self.init_components(**properties)

    # 1. Stretch the top panel across the full screen
    self.flow_panel_1.role = 'full-width-row'  # Forces full-width stretching

    # 2. Make the left sidebar background maroon
    self.panel_sub_checkboxes.background = "#800020"

    # 3. If your left column/container has a name (e.g. column_panel_1), color it too:
    # self.column_panel_1.background = "#800020"
    
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
        chk = anvil.CheckBox(
          text=loc['name'], 
          checked=True, 
          foreground="white"
        )
        
        chk.set_event_handler('change', self.individual_checkbox_change)

        # Save reference using unique index `idx` as key
        self.location_checkboxes[idx] = {'checkbox': chk, 'location': loc}
        self.panel_sub_checkboxes.add_component(chk)

    self.drop_map_markers()

  @handle("text_box_search", "change")
  def text_box_search_change(self, **event_args):
    """Shows a drop-down list of search results as the user types"""
    query = self.text_box_search.text.lower().strip() if self.text_box_search.text else ""

    # Clear the suggestions list panel
    self.panel_search_results.clear()

    # If search box is empty, hide suggestions and restore category filter
    if not query:
      self.panel_search_results.visible = False
      self.drop_down_category_change()
      return

    self.panel_search_results.visible = True
    matches_found = 0

    for idx, loc in enumerate(self.locations):
      location_name = loc.get('name', '').lower()

      if query in location_name:
        matches_found += 1
        # Create a clickable Link for each matching result
        link = anvil.Link(text=loc['name'], foreground="white", role="search-result")

        # When clicked, highlight this exact location with its custom interactive marker
        link.set_event_handler('click', lambda loc=loc, **ea: self.select_search_location(loc))

        self.panel_search_results.add_component(link)

        # Limit to top 5 results so mobile screens aren't cluttered
        if matches_found >= 5:
          break

  def select_search_location(self, loc):
    """Called when user clicks a search result from the dropdown list"""
    # 1. Hide search results list & clear query
    if hasattr(self, 'panel_search_results'):
      self.panel_search_results.clear()
      self.panel_search_results.visible = False

    # 2. Clear existing map pins
    self.map_campus.clear()

    # 3. Safely extract coordinates (handles floats, strings, or missing keys)
    lat = float(loc.get('lat') or loc.get('latitude') or 0)
    lng = float(loc.get('lng') or loc.get('longitude') or loc.get('long') or 0)

    # 4. Drop the interactive marker
    self.drop_single_interactive_marker(loc)

    # 5. Zoom and center map on selected landmark
    if lat != 0 and lng != 0:
      self.map_campus.center = GoogleMap.LatLng(lat, lng)
      self.map_campus.zoom = 17

  def drop_single_interactive_marker(self, loc):
    """Creates and drops a single custom interactive marker"""
    # Extract coordinates
    lat = float(loc.get('lat') or loc.get('latitude') or 0)
    lng = float(loc.get('lng') or loc.get('longitude') or loc.get('long') or 0)

    if lat == 0 or lng == 0:
      return

    name = loc.get('name') or loc.get('title') or "Campus Location"

    # Handle custom icon (supports URL strings, file assets, or Data Table media objects)
    icon_val = loc.get('icon') or loc.get('icon_url')
    icon_url = None

    if isinstance(icon_val, str):
      icon_url = icon_val
    elif hasattr(icon_val, 'url'):  # If stored as a Media Object in Data Tables
      icon_url = icon_val.url

    # Construct Google Map Marker
    marker_kwargs = {
      'position': GoogleMap.LatLng(lat, lng),
      'title': name
    }
    if icon_url:
      marker_kwargs['icon'] = icon_url

    marker = GoogleMap.Marker(**marker_kwargs)

    # Attach click handler safely if marker_click method exists
    if hasattr(self, 'marker_click'):
      marker.set_event_handler('click', lambda **ea: self.marker_click(loc))

    self.map_campus.add_component(marker)



  
  @handle("text_box_search", "pressed_enter")
  def text_box_search_pressed_enter(self, **event_args):
    """Triggers search when Enter is pressed"""
    self.text_box_search_change(**event_args)

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

  
