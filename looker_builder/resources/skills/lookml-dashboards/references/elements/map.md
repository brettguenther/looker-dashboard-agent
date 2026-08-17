# LookML Dashboard Element Vis Config: Maps (Google Maps, Mapbox)

This reference provides exact visualization configuration options for Map chart elements in LookML dashboards.

## Options Reference Table

| Option Key / Path | Type | Label | Description |
| :--- | :--- | :--- | :--- |
| `draw_map_labels_above_data` | `boolean (yes/no)` | `Draw Map Labels Above Data` | Render map region/city labels on top of data layers |
| `elevation_scale` | `number` | `Elevation Scale` | Multiplier for 3D elevation height in 3D heatmap plots |
| `heatmap_gridlines` | `boolean (yes/no)` | `Heatmap Gridlines` | Toggle visibility of gridlines on heatmaps |
| `heatmap_gridlines_empty` | `boolean (yes/no)` | `Gridlines on Empty Regions` | Render gridlines over areas without data points |
| `heatmap_intensity` | `number` | `Intensity` | Brightness / density multiplier for heatmap points |
| `heatmap_opacity` | `number` | `Heatmap Opacity` | Opacity value (0.0 to 1.0) for heatmap layer |
| `heatmap_threshold` | `number` | `Threshold` | Cutoff threshold for heatmap data rendering |
| `hexagon_radius` | `number` | `Hexagon Radius` | Size of hex bins in hexagonal grid maps |
| `hide_legend` | `boolean (yes/no)` | `Hide Legend` | Toggle option to hide map legend |
| `map_bicycling_layer` | `boolean (yes/no)` | `Bicycling Layer` | Show Google Maps bicycling overlay |
| `map_dual_axis` | `boolean (yes/no)` | `Dual-axis Map` | Enable dual-metric map rendering |
| `map_kml_layer` | `boolean (yes/no)` | `KML Layer` | Enable custom KML overlay layer |
| `map_kml_url` | `string` | `KML URL` | URL pointing to external KML file for custom boundaries |
| `map_latitude` | `number` | `Latitude` | Initial center latitude coordinate |
| `map_longitude` | `number` | `Longitude` | Initial center longitude coordinate |
| `map_marker_color_mode` | `string (one of: 'value', 'fixed')` | `Marker Color Mode` | Color markers dynamically by value or fixed palette |
| `map_marker_icon_name` | `string` | `Icon` | Custom icon identifier for map points |
| `map_marker_proportional_scale_type` | `string (one of: 'linear', 'log')` | `Scale` | Scaling function for proportional point markers |
| `map_marker_radius_fixed` | `number` | `Fixed Radius` | Fixed pixel radius for map markers |
| `map_marker_radius_max` | `number` | `Maximum Radius` | Maximum radius cap for value-scaled point markers |
| `map_marker_radius_min` | `number` | `Minimum Radius` | Minimum radius floor for value-scaled point markers |
| `map_marker_radius_mode` | `string (one of: 'proportional_value', 'equal_to_value', 'fixed')` | `Radius` | Radius calculation mode for markers |
| `map_marker_type` | `string (one of: 'circle', 'icon', 'circle_and_icon', 'none')` | `Type` | Shape style for point markers |
| `map_marker_units` | `string (one of: 'meters', 'pixels')` | `Radius Units` | Measurement unit for marker radius |
| `map_pannable` | `boolean (yes/no)` | `Allow Panning` | Allow user to drag and pan map |
| `map_plot_mode` | `string (one of: 'points', 'automagic_heatmap', 'heatmap', 'lines', 'areas', '3d_heatmap')` | `Plot Mode` | Visualization geometry type for map |
| `map_position` | `string (one of: 'fit_data', 'custom')` | `Map Position` | Auto-fit bounds to data points or use custom lat/long |
| `map_tile_provider` | `string (one of: 'light', 'light_no_labels', 'dark', 'dark_no_labels', 'satellite', 'satellite_streets', 'streets', 'outdoors', 'traffic_day', 'traffic_night', 'minimal')` | `Map Style` | Tile background theme style |
| `map_traffic_layer` | `boolean (yes/no)` | `Traffic Layer` | Show Google Maps real-time traffic layer |
| `map_transit_layer` | `boolean (yes/no)` | `Transit Layer` | Show Google Maps transit line overlay |
| `map_value_scale_clamp_max` | `number` | `Maximum Value` | Value clamp upper limit for color scale |
| `map_value_scale_clamp_min` | `number` | `Minimum Value` | Value clamp lower limit for color scale |
| `map_zoom` | `number` | `Zoom Level` | Initial zoom level integer (0 = world, 18 = street) |
| `map_zoomable` | `boolean (yes/no)` | `Allow Zooming` | Allow user to zoom in and out |
| `quantize_map_value_colors` | `boolean (yes/no)` | `Quantize Colors` | Group continuous values into discrete color bands |
| `reverse_map_value_colors` | `boolean (yes/no)` | `Reverse Color Scale` | Invert direction of value color gradient |
| `series_colors.<series_id>` | `string` | `Color Overrides` | Custom hex color for a specific map layer |
| `show_legend` | `boolean (yes/no)` | `Show Legend` | Show or hide map legend |
| `show_region_field` | `boolean (yes/no)` | `Show Region Field in Tooltip` | Display region field inside hover tooltip |
| `show_view_names` | `boolean (yes/no)` | `Show Full Field Name` | Show full field name in tooltip |
