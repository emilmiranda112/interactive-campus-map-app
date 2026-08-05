from ._anvil_designer import Form1Template
import anvil.server
from anvil import *
import anvil.js
from anvil.js import call


class Form1(Form1Template):
  def __init__(self, **properties):
    self.init_components()

    
    # Make the filter drawer background maroon.
    self.panel_sub_checkboxes.background = "#800020"
    
    self.map_markers = []
    self.user_marker = None
    self.location_checkboxes = {}
    self.campus_map = None
    
    self.active_categories = set()
    # Fetch dataset from DataParser backend.
    self.locations = anvil.server.call('load_campus_data')

    # Populate main category dropdown dynamically.
    categories = sorted(list(set(loc.get('category', '').strip() for loc in self.locations if loc.get('category'))))
    self.drop_down_category.items = [("Select a category...", None)] + [(cat, cat) for cat in categories]

  @handle("", "show")
  def form_show(self, **event_args):
    if self.campus_map is not None:
      return

    map_config = anvil.server.call('get_maps_browser_config')
    self.campus_map = call(
      'createCampusMap',
      anvil.js.get_dom_node(self.map_campus),
      map_config,
    )
    self.start_user_tracking()

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

    user_icon = {
      'url': "_/theme/BlueUserMarker.png",
      'scaled_size': [60, 60]  
    }

    # If user marker doesn't exist yet, create it
    if self.user_marker is None:
      self.user_marker = call(
        'addCampusMarker',
        self.campus_map,
        lat,
        lng,
        "You are here!",
        user_icon,
        None,
      )
    else:
      call('updateCampusMarkerPosition', self.user_marker, lat, lng)

  def handle_location_error(self, error, **event_args):
    """Handles GPS permission denial or timeouts gracefully."""
    print("Could not retrieve user location:", error.message)
    # Draw checklist markers even when location permission is unavailable.
    self.drop_map_markers()

  @handle("drop_down_category", "change")
  def drop_down_category_change(self, **event_args):
    """Triggered when user selects a category (e.g., Restrooms, Sports)"""
    selected_cat = self.drop_down_category.selected_value

    # Clear ONLY the sub-checkbox UI panel (do not clear self.location_checkboxes)
    self.panel_sub_checkboxes.clear()

    if not selected_cat:
      self.drop_map_markers()
      return

    for idx, loc in enumerate(self.locations):
      if loc.get('category', '').strip() == selected_cat:

        # Check if we already created a checkbox for this location
        if idx in self.location_checkboxes:
          chk = self.location_checkboxes[idx]['checkbox']
        else:
          # First time seeing this location, create a new CheckBox
          chk = anvil.CheckBox(
            text=loc['name'],
            checked=True,
            foreground="white"
          )
          chk.set_event_handler('change', self.individual_checkbox_change)

          # Store it permanently in our tracking dictionary
          self.location_checkboxes[idx] = {'checkbox': chk, 'location': loc}

          # Add the checkbox to the active category UI panel
        self.panel_sub_checkboxes.add_component(chk)

    # Refresh markers so all currently checked items across categories display
    self.drop_map_markers()

  @handle("text_box_search", "change")
  def text_box_search_change(self, **event_args):
    """Shows a drop-down list of search results as the user types"""
    query = self.text_box_search.text.lower().strip() if self.text_box_search.text else ""
    self.text_box_search.foreground = "#800000"
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
    """Called when user taps an item from the search dropdown"""
    self.panel_search_results.clear()
    self.panel_search_results.visible = False
    self.clear_map_markers()

    # Delegate interactive marker creation
    self.drop_single_interactive_marker(loc)

    # Adjust map camera center & zoom safely
    lat = float(loc.get('lat') or loc.get('latitude') or 0)
    lng = float(loc.get('lng') or loc.get('longitude') or loc.get('long') or 0)
    if lat != 0 and lng != 0:
      call('centerCampusMap', self.campus_map, lat, lng, 19)

  def drop_single_interactive_marker(self, loc):
    """Creates and drops a single custom interactive marker"""
    lat = float(loc.get('lat') or loc.get('latitude') or 0)
    lng = float(loc.get('lng') or loc.get('longitude') or loc.get('long') or 0)

    if lat == 0 or lng == 0:
      return

    name = loc.get('name') or loc.get('title') or "Campus Location"
    desc = loc.get('description') or loc.get('desc') or "No description available."

    # Handle custom icon logic...
    icon_val = loc.get('icon') or loc.get('icon_url')
    icon_url = None
    if isinstance(icon_val, str):
      icon_url = icon_val
    elif hasattr(icon_val, 'url'):
      icon_url = icon_val.url

    self.add_location_marker(lat, lng, name, desc, icon_url)

  
  @handle("text_box_search", "pressed_enter")
  def text_box_search_pressed_enter(self, **event_args):
    """Triggers search when Enter is pressed"""
    self.text_box_search_change(**event_args)

  def individual_checkbox_change(self, **event_args):
    """Triggered whenever any sub-checkbox is checked or unchecked"""
    self.drop_map_markers()

  def drop_map_markers(self):
    # Define icon styles & sizes
    category_icons = {
      "Restrooms": {
        'url': "_/theme/BlueRestroomIcon.png",
        'scaled_size': [35, 30]
      },
      "Sports": {
        'url': "_/theme/RunIcon.png",
        'scaled_size': [30, 30]
      },
      "Classrooms": {
        'url': "_/theme/ClassroomIcon.png",
        'scaled_size': [30, 30]
      },
      "Academic & Culture": {
        'url': "_/theme/BookIcon.png",
        'scaled_size': [30, 30]
      },
      "Cafeteria": {
        'url': "_/theme/FoodIcon.png",
        'scaled_size': [30, 30]
      },
      "Parking": {
        'url': "_/theme/ParkingIcon.png",
        'scaled_size': [30, 30]
      },
      "Office and Facilities": {
        'url': "_/theme/OfficeIcon.png",
        'scaled_size': [30, 30]
      },
      "200's Quad": "http://maps.google.com/mapfiles/ms/icons/purple-dot.png",
      "300's Quad": "http://maps.google.com/mapfiles/ms/icons/orange-dot.png",
      "700's Quad": "http://maps.google.com/mapfiles/ms/icons/yellow-dot.png",
    }
      
    

    self.clear_map_markers()

    # Only draw markers whose specific sub-checkbox is checked.
    for key, item in self.location_checkboxes.items():
      if item['checkbox'].checked:
        loc = item['location']
        category = loc.get('category', '').strip()
        chosen_icon = category_icons.get(category, "http://maps.google.com/mapfiles/ms/icons/red-dot.png")

        self.add_location_marker(
          float(loc['lat']),
          float(loc['lng']),
          loc['name'],
          loc['desc'],
          chosen_icon,
        )

  def clear_map_markers(self):
    for marker in self.map_markers:
      call('removeCampusMarker', marker)
    self.map_markers = []

  def add_location_marker(self, lat, lng, name, description, icon=None):
    marker = call(
      'addCampusMarker',
      self.campus_map,
      lat,
      lng,
      name,
      icon,
      anvil.js.report_exceptions(
        lambda event: self.marker_click(name, description)
      ),
    )
    self.map_markers.append(marker)

  def marker_click(self, name, description):
    """Show the selected location's description."""
    alert(content=description, title=name)


  
  def select_current_category(self, select_state=True):
    """Checks or unchecks ONLY the items in the active category dropdown."""
    current_cat = self.drop_down_category.selected_value
    if not current_cat:
      return

    for item in self.location_checkboxes.values():
      if item['location'].get('category', '').strip() == current_cat:
        item['checkbox'].checked = select_state

    self.drop_map_markers()


  def deselect_current_category(self):
    """Unchecks ONLY the items in the currently active category."""
    self.select_current_category(select_state=False)
  

  def clear_all_markers(self):
    """Unchecks ALL checkboxes across ALL categories and wipes the map."""
    for item in self.location_checkboxes.values():
      item['checkbox'].checked = False

    # Redraw the map (which will now draw 0 markers)
    self.drop_map_markers()
    

  @handle("btn_select_all_click", "click")
  def btn_select_all_click_click(self, **event_args):
    """Triggered when Select All Category button is clicked."""
    self.select_current_category(True)
  

  @handle("btn_clear_all_click", "click")
  def btn_clear_all_click_click(self, **event_args):
    """Triggered when Clear Map button is clicked."""
    self.clear_all_markers()

  @handle("btn_deselect_category", "click")
  def btn_deselect_category_click(self, **event_args):
    """Deselects all items in the current category."""
    self.deselect_current_category()
