# LookML Dashboard Element Vis Config: Conditional Formatting Rule Syntax

This reference provides exact YAML properties, structure, and examples for writing conditional formatting rules in LookML dashboard element definitions.

## Option Key: `conditional_formatting`
Type: `list of CFRule objects`

## CFRule YAML Properties

| Property Key | Type | Description |
| :--- | :--- | :--- |
| `id` | `string` | Optional. Unique UUID generated to track the rule. |
| `type` | `string (one of: 'along a scale...', 'equal to', 'not equal to', 'greater than', 'less than', 'between', 'not between', 'starts with', 'contains', 'null', 'not null', 'low to high', 'high to low')` | The comparison operator or scale rule type. |
| `value` | `any` | Comparison value (numeric, or array for range operators like 'between'). |
| `stringValue` | `string` | Comparison string value (used for string operators like 'contains', 'starts with'). |
| `fields` | `list of strings` | List of field names (e.g. `["orders.count"]`) this rule applies to. If empty, applies based on `apply_to`. |
| `apply_to` | `string (one of: 'selectFields', 'allNumericFields', 'allStringFields')` | Determines target fields for the rule. |
| `apply_formatting_to_row` | `boolean (yes/no)` | If yes, highlights entire row. If no, highlights individual cell. |
| `cell_format` | `CFStyle map/object` | Formatting style applied to individual cell. |
| `row_format` | `CFStyle map/object` | Formatting style applied to entire row. |

### CFStyle YAML Properties

| Property Key | Type | Description |
| :--- | :--- | :--- |
| `background_color` | `string` | Background color hex code (e.g., `"#1A73E8"`). |
| `font_color` | `string` | Font color hex code. |
| `font_style` | `map/object` | Font style toggles: `bold` (boolean), `italic` (boolean), `strikethrough` (boolean). |
| `color_application` | `map/object` | Theme color collection: `collection_id` (string), `palette_id` (string), `options` (map with `mirror`, `reverse`, `stepped`). |

## Concrete YAML Example

```yaml
conditional_formatting:
  - type: greater than
    value: 100
    fields:
      - orders.count
    apply_to: selectFields
    apply_formatting_to_row: no
    cell_format:
      background_color: "#F3F3F3"
      font_color: "#FF0000"
      font_style:
        bold: yes
        italic: no
        strikethrough: no
```
