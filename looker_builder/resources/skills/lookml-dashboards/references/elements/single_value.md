# LookML Dashboard Element Vis Config: Single Value

This reference provides exact visualization configuration options for Single Value elements in LookML dashboards.

## Options Reference Table

| Option Key / Path | Type | Label | Description |
| :--- | :--- | :--- | :--- |
| `comparison_type` | `string (one of: 'change', 'progress_percentage')` | `Comparison Type` | Comparison calculation method (e.g., period-over-period change) |
| `comparison_label` | `string` | `Comparison Label` | Custom text label accompanying comparison calculation |
| `comparison_reverse_colors` | `boolean (yes/no)` | `Positive Values are Bad` | Swap positive/negative indicator colors |
| `show_comparison` | `boolean (yes/no)` | `Show Comparison` | Toggle visibility of comparison value |
| `show_comparison_label` | `boolean (yes/no)` | `Show Comparison Label` | Toggle visibility of comparison label text |
| `conditional_formatting_include_nulls_as_zero` | `boolean (yes/no)` | `Include Null Values as Zero` | Treat null values as zero in conditional formatting |
| `custom_color` | `string` | `Value Color` | Hex color code specifying text color of primary value display |
| `enable_conditional_formatting` | `boolean (yes/no)` | `Enable Conditional Formatting` | Enable conditional formatting rules |
| `show_single_value_title` | `boolean (yes/no)` | `Show Title` | Toggle visibility of element title |
| `single_value_title` | `string` | `Title Override` | Custom text override for element title |
| `smart_single_value_size` | `boolean (yes/no)` | `Auto Resize Value` | Automatically scale text size to fit tile bounds |
| `value_format` | `string` | `Value Format` | Numeric display format pattern (e.g., `"$#,##0.00"`) |
