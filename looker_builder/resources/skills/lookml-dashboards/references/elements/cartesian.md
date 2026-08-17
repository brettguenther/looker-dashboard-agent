# LookML Dashboard Element Vis Config: Cartesian (Line, Bar, Column, Area, Scatter, Waterfall, Boxplot)

This reference provides exact visualization configuration options for Cartesian chart elements in LookML dashboards.

## Options Reference Table

| Option Key / Path | Type | Label | Description |
| :--- | :--- | :--- | :--- |
| `cluster_points` | `boolean (yes/no)` | `Cluster Points` | Toggle to group or cluster data points in a scatter chart visualization |
| `color_application.options.reverse` | `boolean (yes/no)` | `Reverse colors` | Toggle to reverse the order of colors in the selected categorical palette |
| `column_group_spacing_ratio` | `number` | `Spacing` | Spacing between column groups or columns |
| `column_spacing_ratio` | `number` | `Inner Spacing` | Spacing between columns within a column group |
| `custom_quadrant_point_x` | `number` | `Custom Quadrant Point X` | Custom quadrant coordinate slider for X axis |
| `custom_quadrant_point_y` | `number` | `Custom Quadrant Point Y` | Custom quadrant coordinate slider for Y axis |
| `custom_quadrant_value_x` | `number` | `Value` | Coordinate numerical value for custom quadrant points on X axis |
| `custom_quadrant_value_y` | `number` | `Value` | Coordinate numerical value for custom quadrant points on Y axis |
| `discontinuous_nulls` | `boolean (yes/no)` | `Display Null Values as Discontinuities` | Display null values as discontinuities in line/area charts |
| `down_color` | `string` | `Down Color` | Hex color code for negative/downward series in waterfall charts |
| `font_size` | `string` | `Font Size` | Font size configuration for axis/data labels |
| `hide_legend` | `boolean (yes/no)` | `Hide Legend` | Toggle option to hide chart legend |
| `interpolation` | `string (one of: 'linear', 'monotone', 'step')` | `Line Interpolation` | Style for drawing lines between points |
| `label_rotation` | `number` | `Value Rotation` | Rotation angle in degrees for axis labels |
| `label_value_format` | `string` | `Value Format` | Value format string pattern for data point labels |
| `legend_position` | `string (one of: 'left', 'center', 'right')` | `Legend Alignment` | Alignment position of the legend |
| `point_style` | `string (one of: 'none', 'circle', 'circle_outline')` | `Point Style` | Marker style for points on line, area, and scatter charts |
| `quadrant_properties.[i].color` | `string` | `Color` | Hex color code for a specific quadrant background |
| `quadrant_properties.[i].label` | `string` | `Label` | Text label for a specific quadrant |
| `quadrants_enabled` | `boolean (yes/no)` | `Plot Quadrants` | Toggle option to show quadrants in scatter chart |
| `series_colors.<series_id>` | `string` | `Color Overrides` | Hex color code specifying custom color override for a specific data series |
| `series_labels.<series_id>` | `string` | `Label` | Custom label for a specific series in a Cartesian chart |
| `series_point_styles.<series_id>` | `string (one of: 'circle', 'square', 'triangle', 'diamond', 'automatic')` | `Point Shapes Overrides` | Custom point shape style for a specific data series |
| `series_types.<series_id>` | `string (one of: 'line', 'column', 'bar', 'area', 'scatter', 'pie')` | `Type` | Chart type override for a specific data series (for mixed-series charts) |
| `show_dropoff` | `boolean (yes/no)` | `Show Percent of Previous` | Display arrows showing percent change from previous value |
| `show_null_labels` | `boolean (yes/no)` | `Label Null Values` | Show value labels for null data points |
| `show_null_points` | `boolean (yes/no)` | `Plot Null Values` | Plot null values in a graph visualization |
| `show_silhouette` | `boolean (yes/no)` | `Show Silhouette` | Display a grey silhouette for series disabled in legend |
| `show_totals_labels` | `boolean (yes/no)` | `Totals Labels` | Show or hide labels for the totals of stacked series |
| `show_value_labels` | `boolean (yes/no)` | `Label Values` | Show value labels for each data point |
| `show_view_names` | `boolean (yes/no)` | `Show Full Field Name` | Toggle to show full field name in tooltip |
| `show_x_axis_label` | `boolean (yes/no)` | `Show Axis Name` | Toggle to show the X axis name |
| `show_x_axis_ticks` | `boolean (yes/no)` | `Show Axis Value Labels` | Toggle to show X axis value labels (ticks) |
| `show_y_axis_labels` | `boolean (yes/no)` | `Show Y Axis Name` | Toggle option to show or hide title label of Y axis |
| `show_y_axis_ticks` | `boolean (yes/no)` | `Show Y Axis Value Labels` | Toggle option to show or hide tick values along Y axis |
| `stacking` | `string (one of: '', 'normal', 'percent')` | `Series Positioning` | Stacking style for bar/column/area charts |
| `swap_axes` | `boolean (yes/no)` | `Swap X and Y Axis` | Toggle to swap X and Y axis |
| `total_color` | `string` | `Total Color` | Hex color code for totals bars in waterfall/column charts |
| `totals_rotation` | `number` | `Totals Rotation` | Rotation angle in degrees for totals labels |
| `trellis` | `string (one of: '', 'group', 'row', 'col')` | `Grid Layout` | Split chart into a Trellis grid layout |
| `trend_lines.[i].label_position` | `string` | `Label Position` | Position of the trend line label |
| `trend_lines.[i].label_type` | `string` | `Label Type` | Type of trend line label |
| `trend_lines.[i].regression_type` | `string (one of: 'linear', 'exponential', 'logarithmic', 'power', 'polynomial', 'moving_average')` | `Trend Type` | Type of trend line regression |
| `trend_lines.[i].series_index` | `number` | `Series Index` | Series index the trend line applies to |
| `trend_lines.[i].show_label` | `boolean (yes/no)` | `Show Label` | Toggle to show trend line label |
| `up_color` | `string` | `Up Color` | Hex color code for positive/upward series in waterfall charts |
| `x_axis_label_rotation` | `number` | `Label Rotation` | Rotation angle in degrees for X axis labels |
| `x_axis_datetime_label` | `string` | `Time Label Format` | Format pattern for datetime labels on X axis |
| `x_axis_gridlines` | `boolean (yes/no)` | `Show Gridlines` | Toggle to show X axis gridlines |
| `x_axis_label` | `string` | `Custom Axis Name` | Custom text name for X axis |
| `x_axis_reversed` | `boolean (yes/no)` | `Reverse Axis` | Toggle direction of X axis |
| `x_axis_scale` | `string (one of: 'auto', 'ordinal', 'time')` | `Scale Type` | Scale type for X axis |
| `x_axis_zoom` | `boolean (yes/no)` | `Allow Zoom` | Enable zoom to magnify a portion of the chart |
| `y_axes.[i].orientation` | `string (one of: 'left', 'right', 'top', 'bottom')` | `Orientation` | Y axis position orientation |
| `y_axes.[i].label` | `string` | `Axis Name` | Custom label for Y axis |
| `y_axes.[i].maxValue` | `number` | `Max Value` | Maximum numeric bound for Y axis |
| `y_axes.[i].minValue` | `number` | `Min Value` | Minimum numeric bound for Y axis |
| `y_axes.[i].showLabels` | `boolean (yes/no)` | `Show Axis Name` | Toggle to show Y axis name |
| `y_axes.[i].showValues` | `boolean (yes/no)` | `Show Axis Value Labels` | Toggle to show Y axis tick values |
| `y_axes.[i].tickDensity` | `string (one of: 'default', 'custom')` | `Tick Density` | Tick density calculation style |
| `y_axes.[i].tickDensityCustom` | `number` | `Custom Tick Density` | Custom step value / count for Y axis ticks |
| `y_axes.[i].type` | `string (one of: 'linear', 'log')` | `Scale Type` | Numeric scale type for Y axis |
| `y_axes.[i].unpinAxis` | `boolean (yes/no)` | `Unpin Axis` | Unpin axis from starting at zero |
| `y_axes.[i].valueFormat` | `string` | `Y Axis Format` | Format string for Y axis tick labels |
| `y_axis_gridlines` | `boolean (yes/no)` | `Show Gridlines` | Toggle to show Y axis gridlines |
| `y_axis_reversed` | `boolean (yes/no)` | `Reverse Axes` | Toggle direction of Y axis |
| `y_axis_tick_density` | `string (one of: 'default', 'custom')` | `Tick Density` | Tick interval calculation method |
| `y_axis_tick_density_custom` | `number` | `Custom Tick Density` | Step size for Y axis ticks |
| `y_axis_zoom` | `boolean (yes/no)` | `Allow Zoom` | Enable zoom to magnify a portion of chart |

## Usage Guidelines for AI Agents

1. **Flat Structure**: Write options flat at the element level in LookML dashboard YAML files. Do NOT wrap them in a `vis_config` block.
2. **Expand YAML**: Expand dot-separated paths (e.g., `color_application.options.reverse`) into nested YAML blocks or inline maps:
   ```yaml
   color_application:
     options:
       reverse: true
   ```
3. **YAML Lists**: For paths containing list indices `[i]` (e.g., `y_axes.[i].label`, `trend_lines.[i].show_label`), expand them into YAML lists:
   ```yaml
   y_axes:
     - label: "Left Axis"
       orientation: left
   ```
4. **Series Placeholders**: Replace `<series_id>` with the exact measure or dimension identifier (e.g., `orders.count`):
   ```yaml
   series_labels:
     orders.count: "Total Orders"
   ```
