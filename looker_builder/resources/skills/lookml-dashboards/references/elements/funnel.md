# LookML Dashboard Element Vis Config: Funnel and Stepped Funnel

This reference provides exact visualization configuration options for Funnel chart elements in LookML dashboards.

## Options Reference Table

| Option Key / Path | Type | Label | Description |
| :--- | :--- | :--- | :--- |
| `isStepped` | `boolean (yes/no)` | `Stepped Funnel` | Toggle between smooth funnel and stepped funnel |
| `labelColor` | `string` | `Label Color` | Custom hex color code for labels |
| `labelColorEnabled` | `boolean (yes/no)` | `Color Label` | Enable custom label coloring |
| `labelOverlap` | `boolean (yes/no)` | `Allow Label Overlap` | Toggle to allow overlapping labels |
| `labelPosition` | `string (one of: 'left', 'right', 'center', 'inline')` | `Label Position` | Position alignment for funnel step labels |
| `labelScale` | `number` | `Label Scale` | Scale multiplier for label font sizes |
| `leftAxisLabel` | `string` | `Left Axis Label` | Custom text label for left axis |
| `leftAxisLabelVisible` | `boolean (yes/no)` | `Label Left Axis` | Toggle visibility of left axis label |
| `orientation` | `string (one of: 'vertical', 'horizontal')` | `Orientation` | Direction orientation of the funnel |
| `percentPosition` | `string (one of: 'inline', 'hidden', 'left', 'right')` | `Percent Position` | Position of percentage display values |
| `percentType` | `string (one of: 'prior_step', 'total')` | `Percent Type` | Calculate percentage relative to prior step or total baseline |
| `rightAxisLabel` | `string` | `Right Axis Label` | Custom text label for right axis |
| `rightAxisLabelVisible` | `boolean (yes/no)` | `Label Right Axis` | Toggle visibility of right axis label |
| `smoothedBars` | `boolean (yes/no)` | `Smoothed Bars` | Toggle smooth curvature on funnel bars |
| `valuePosition` | `string (one of: 'inline', 'hidden', 'left', 'right')` | `Value Position` | Position of raw value displays |
