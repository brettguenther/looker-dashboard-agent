# LookML Dashboard Element Vis Config: KPI (Key Performance Indicator)

This reference provides exact visualization configuration options for KPI elements in LookML dashboards.

## Options Reference Table

| Option Key / Path | Type | Label | Description |
| :--- | :--- | :--- | :--- |
| `alignment` | `string (one of: 'left', 'center', 'right')` | `Alignment` | Horizontal alignment of KPI value and text |
| `comparison_type` | `string (one of: 'change', 'progress_percentage')` | `Comparison Type` | Comparison calculation method (e.g., period-over-period change or progress vs goal) |
| `comparison_label` | `string` | `Comparison Label` | Custom text label accompanying comparison calculation |
| `comparison_reverse_colors` | `boolean (yes/no)` | `Positive Values are Bad` | Swap red/green indicator colors (set to true when lower values are better) |
| `show_comparison` | `boolean (yes/no)` | `Show Comparison` | Toggle visibility of comparison value |
| `show_comparison_label` | `boolean (yes/no)` | `Show Comparison Label` | Toggle visibility of comparison label text |
| `comparison_row` | `number` | `Comparison Row` | Row index in query results used for comparison offset |
| `comparison_series` | `string` | `Comparison Series` | Series identifier used for comparison offset |
| `conditional_formatting_include_nulls_as_zero` | `boolean (yes/no)` | `Include Null Values as Zero` | Treat null values as zero in conditional formatting rules |
| `custom_color` | `string` | `Value Color` | Hex color code specifying text color of primary KPI value display |
| `enable_conditional_formatting` | `boolean (yes/no)` | `Enable Conditional Formatting` | Enable conditional formatting rules |
| `kpi_chart_type` | `string` | `Chart Type` | Visualization sub-type for embedded sparkline/trend |
| `show_chart_component` | `boolean (yes/no)` | `Show Chart Component` | Toggle visibility of embedded mini sparkline/trend chart |
| `show_single_value_title` | `boolean (yes/no)` | `Show Title` | Toggle visibility of element title |
| `single_value_title` | `string` | `Title Override` | Custom text override for element title |
| `smart_single_value_size` | `boolean (yes/no)` | `Auto Resize Value` | Automatically scale text size to fit tile bounds |
| `value_format` | `string` | `Value Format` | Numeric display format pattern (e.g., `"$#,##0.00"`) |
| `visible_x_axis` | `boolean (yes/no)` | `Visible X Axis` | Toggle visibility of X axis on embedded mini chart |
