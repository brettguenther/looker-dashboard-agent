# LookML Dashboard Element Vis Config: Table and Grid

This reference provides exact visualization configuration options for Table and Grid elements in LookML dashboards.

## Options Reference Table

| Option Key / Path | Type | Label | Description |
| :--- | :--- | :--- | :--- |
| `conditional_formatting_include_nulls` | `boolean (yes/no)` | `Include Null Values as Zero` | Include null values as zero in conditional formatting calculations |
| `conditional_formatting_include_totals` | `boolean (yes/no)` | `Include Totals` | Include summary totals rows in conditional formatting rules |
| `enable_conditional_formatting` | `boolean (yes/no)` | `Enable Conditional Formatting` | Toggle conditional formatting rules |
| `header_background_color` | `string` | `Header Background Color` | Hex color code for table header background |
| `header_font_color` | `string` | `Header Font Color` | Hex color code for table header text |
| `header_font_size` | `string (e.g. 'medium', 'small', 'large')` | `Header Font Size` | Font size configuration for header row |
| `header_text_alignment` | `string (one of: 'left', 'center', 'right')` | `Header Alignment` | Text alignment for header text |
| `minimum_column_width` | `number` | `Minimum Column Width` | Minimum width in pixels for table columns |
| `row_groups.configurable_subtotals` | `boolean (yes/no)` | `Show Subtotal Row` | Display subtotal calculation rows for grouped rows |
| `row_groups.default_display_level` | `number` | `Default Display Level` | Default expansion depth level for grouped rows |
| `row_groups.enabled` | `boolean (yes/no)` | `Enable Row Groups` | Enable collapsible row grouping |
| `row_groups.group_column_header` | `string` | `Group Column Header` | Custom column header label for grouped column |
| `row_groups.show_group_counts` | `boolean (yes/no)` | `Show Group Counts` | Display count of rows within each group |
| `row_groups.subtotal_location` | `string (one of: 'bottom', 'top')` | `Subtotal Location` | Render subtotals at top or bottom of group |
| `rows_font_size` | `string (e.g. 'medium', 'small', 'large')` | `Rows Font Size` | Font size configuration for data rows |
| `series_cell_visualizations.<field_name>.is_active` | `boolean (yes/no)` | `Cell Visualization` | Toggle in-cell bar/bullet visualization for numeric field |
| `series_cell_visualizations.<field_name>.value_display` | `boolean (yes/no)` | `Show Value Display` | Show numeric value display alongside cell bar visualization |
| `series_cell_visualizations.<field_name>.value_labels` | `boolean (yes/no)` | `Show Value Labels` | Show numeric value labels alongside cell bar visualization |
| `series_column_widths.<field_name>` | `number` | `Width` | Custom width in pixels for specific column |
| `series_labels.<field_name>` | `string` | `Label` | Custom column header text override |
| `series_text_format.<field_name>.align` | `string (one of: 'left', 'center', 'right')` | `Alignment` | Text alignment for specific column |
| `series_text_format.<field_name>.bg_color` | `string` | `Background Color` | Custom background color for specific column |
| `series_text_format.<field_name>.fg_color` | `string` | `Foreground Color` | Custom text font color for specific column |
| `series_value_format.<field_name>` | `string` | `Value Format` | Numeric format pattern string for specific column |
| `show_row_numbers` | `boolean (yes/no)` | `Show Row Numbers` | Display row index numbers on left edge |
| `show_row_totals` | `boolean (yes/no)` | `Show Row Totals` | Display horizontal row total calculations |
| `show_totals` | `boolean (yes/no)` | `Show Totals` | Display vertical column summary total calculations |
| `show_view_names` | `boolean (yes/no)` | `Show Full Field Name` | Show full view and field name in column headers |
| `size_to_fit` | `boolean (yes/no)` | `Size Columns to Fit` | Auto-stretch columns to fill table container width |
| `table_column_hover_highlight_enable` | `boolean (yes/no)` | `Enable Hover Highlighting` | Highlight row/column on mouse hover |
| `table_custom_border_color` | `string` | `Border Color` | Hex color code for cell grid borders |
| `table_custom_border_enable` | `boolean (yes/no)` | `Custom Borders` | Enable custom border styling |
| `table_custom_border_style` | `string (one of: 'solid', 'dashed', 'dotted')` | `Border Style` | Line style of table borders |
| `table_custom_border_width` | `number` | `Border Width` | Width in pixels of table borders |
| `table_enable_pagination` | `boolean (yes/no)` | `Enable Pagination` | Enable paged table navigation |
| `table_page_size_options` | `string` | `Page Size Options` | Comma-separated page size choices (e.g. `"10,25,50"`) |
| `table_show_footer` | `boolean (yes/no)` | `Show Footer` | Display table footer bar |
| `table_show_headers` | `boolean (yes/no)` | `Show Headers` | Show or hide table header row |
| `table_theme` | `string (one of: 'white', 'editable', 'gray', 'unstyled')` | `Table Theme` | Pre-styled theme palette for table |
| `transpose` | `boolean (yes/no)` | `Transpose` | Swap rows and columns |
| `truncate_header` | `boolean (yes/no)` | `Truncate Column Names` | Truncate long column names with ellipsis |
| `truncate_text` | `boolean (yes/no)` | `Truncate Text` | Truncate long cell text values with ellipsis |
