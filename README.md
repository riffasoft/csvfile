# csvfile
A powerful and flexible Python class for handling CSV files with automatic encoding detection, delimiter detection, type casting, and advanced data manipulation capabilities.


## Features

- 🔍 **Auto-detection** of encoding and delimiter
- 🏷️ **Header normalization** and automatic type casting
- 📝 **Read and write** operations with consistent formatting
- 🔍 **Advanced filtering** with multiple conditions
- ✏️ **Update, add, and delete** rows with automatic saving
- 🎯 **Flexible column access** by header name or index
- 🛡️ **Robust error handling** for malformed data

## Installation

```python
# Simply copy the CSVFile class to your project
from csv_file import CSVFile
```

## Quick Start

### Basic Usage

```python
# Load a CSV file with auto-detection
csv_file = CSVFile("data.csv")

# Display basic info
print(csv_file)
# <CSVFile path=data.csv, rows=100, columns=5, delimiter=','>

# Access headers and data
print("Headers:", csv_file.header)
print("First row:", csv_file.rows[0])
```

### Reading Data

```python
# Load with custom options
csv_file = CSVFile(
    "data.csv",
    has_header=True,           # Default: True
    auto_cast=True,            # Default: True - convert numbers, booleans
    normalize_header=True,     # Default: True - convert to snake_case
    skip_empty=True            # Default: True - skip empty rows
)

# Convert to list of dictionaries
data_dict = csv_file.to_dict()
for row in data_dict:
    print(row)
```

## Advanced Usage

### Filtering Data

```python
# Filter by column value (using header name)
active_users = csv_file.filter_by_column("status", "active")
print(f"Active users: {len(active_users.rows)}")

# Filter by column index
adults = csv_file.filter_by_column(1, 18, ">=")  # column index 1, age >= 18

# Filter with custom condition
def high_value_customer(row, index):
    return row[3] == "premium" and row[4] > 1000  # status and balance
    
high_value = csv_file.filter_rows(high_value_customer)

# Multiple conditions (AND logic)
conditions = [
    ("status", "active", "=="),
    ("age", 25, ">="),
    ("city", "Jakarta", "==")
]
filtered = csv_file.filter_multiple(conditions)

# Filter empty values
non_empty_emails = csv_file.filter_empty("email")
non_empty_rows = csv_file.filter_empty()  # Remove completely empty rows
```

### Supported Filter Operators

- `==`, `!=`, `>`, `<`, `>=`, `<=` - Comparison operators
- `in`, `not in` - Membership operators  
- `contains` - Substring search
- `startswith`, `endswith` - String operations

### Updating Data

```python
# Update by header name
csv_file.update_row(0, {"name": "John Updated", "age": 31})

# Update by column index
csv_file.update_row(1, {0: "Jane", 1: 28, 2: "Engineer"})

# Update using list (by column order)
csv_file.update_row(2, ["Bob", 35, "Manager", "active"])

# Update single cell
csv_file.update_cell(0, "name", "Johnathan")  # By header name
csv_file.update_cell(0, 0, "Johnathan")       # By column index

# Automatic saving
csv_file.update_row_and_save(0, {"name": "John"}, "updated_data.csv")
csv_file.update_cell_and_save(0, "age", 32)  # Saves to original file
```

### Adding and Deleting Rows

```python
# Add row using header names
csv_file.add_row({"name": "New User", "age": 25, "city": "Bandung"})

# Add row using column indexes
csv_file.add_row({0: "Another User", 1: 30, 2: "Surabaya"})

# Add row using list
csv_file.add_row(["List User", 35, "Jakarta"])

# Add and save immediately
csv_file.add_row_and_save({"name": "Quick Save", "age": 40})

# Delete rows
csv_file.delete_row(0)  # Delete first row
csv_file.delete_row_and_save(1)  # Delete and save
```

### Working with Different File Formats

```python
# Tab-separated files
tsv_file = CSVFile("data.tsv", candidates=["\t"])

# Semicolon-separated (common in Europe)
euro_csv = CSVFile("data_europe.csv", candidates=[";"])

# Pipe-separated files
pipe_file = CSVFile("data.psv", candidates=["|"])

# Multiple delimiter candidates
any_file = CSVFile("unknown_format.txt", candidates=[",", ";", "|", "\t"])
```

### File Operations

```python
# Save to different file
csv_file.save("backup.csv")

# Overwrite original file
csv_file.save()

# After multiple operations, save once
csv_file.update_row(0, {"name": "Updated"})
csv_file.add_row({"name": "New Row"})
csv_file.delete_row(1)
csv_file.save("final_data.csv")
```

## Complete Example

```python
from csv_file import CSVFile

# Create sample data file
sample_data = """name,age,city,status
John,25,Jakarta,active
Jane,30,Bandung,inactive
Bob,22,Jakarta,active
Alice,35,Surabaya,active
Charlie,28,,inactive"""

with open("sample.csv", "w") as f:
    f.write(sample_data)

# Load and process data
csv = CSVFile("sample.csv")

print("Original data:")
for row in csv.to_dict():
    print(row)

# Filter active users in Jakarta
print("\nActive users in Jakarta:")
jakarta_active = csv.filter_multiple([
    ("status", "active", "=="),
    ("city", "Jakarta", "==")
])
for row in jakarta_active.to_dict():
    print(row)

# Update user information
csv.update_row(1, {"age": 31, "status": "active"})
csv.update_cell(4, "city", "Malang")  # Charlie now has a city

# Add new users
csv.add_row({"name": "Diana", "age": 27, "city": "Jakarta", "status": "active"})
csv.add_row({0: "Eve", 1: 29, 2: "Bandung", 3: "active"})

print("\nAfter updates:")
for row in csv.to_dict():
    print(row)

# Save results
csv.save("processed_data.csv")

# Advanced filtering examples
print("\nUsers age 25-30:")
age_25_30 = csv.filter_rows(lambda row, idx: 25 <= row[1] <= 30)
for row in age_25_30.to_dict():
    print(row)

print("\nUsers with 'a' in name:")
name_contains_a = csv.filter_by_column("name", "a", "contains")
for row in name_contains_a.to_dict():
    print(row)


# loop with add and update column
csv_path = "data.csv" 
csvdata = CSVFile(path=csv_path,candidates=",",has_header=False,skip_empty=True)
if csvdata.get_columns_count()==1: csvdata.add_column()
for index,row in csvdata.enumerate_rows():      
    email = row[0]
    password = row[0]
        
    csvdata.update_row(index,[email,"sukses"])
    csvdata.save()


```
## Class Methods Reference

### Initialization
```python
CSVFile(
    path,                     # File path
    candidates=None,          # Delimiter candidates: [",", ";", "|", "\t"]
    has_header=True,          # First row is header
    skip_empty=True,          # Skip empty rows
    auto_cast=True,           # Auto-convert data types
    normalize_header=True     # Normalize header names
)
```

### Core Methods
- `to_dict()` - Convert to list of dictionaries
- `save(path=None)` - Save to file
- `get_columns_count()` - Get number of columns

### Filter Methods
- `filter_rows(condition)` - Filter with custom function
- `filter_by_column(col_identifier, value, operator)` - Filter by column
- `filter_empty(col_identifier=None)` - Filter empty values
- `filter_multiple(conditions)` - Multiple condition filter
- `get_rows_with_indices(condition)` - Get rows with original indices

### Data Manipulation
- `update_row(index, new_data)` - Update entire row
- `update_cell(row_index, col_identifier, value)` - Update single cell
- `add_row(new_data)` - Add new row
- `delete_row(index)` - Delete row

### Auto-save Methods
- `update_row_and_save(index, new_data, path=None)`
- `update_cell_and_save(row_index, col_identifier, value, path=None)`
- `add_row_and_save(new_data, path=None)`
- `delete_row_and_save(index, path=None)`

## Handling Special Cases

### Files without Headers
```python
no_header_csv = CSVFile("data_no_header.csv", has_header=False)
# Access data directly via csv.rows
```

### Custom Encoding
```python
# The class auto-detects encoding, but you can specify:
# UTF-8, UTF-8-sig, Latin-1 are automatically detected
```

### Malformed Data
```python
# The class automatically handles:
# - Inconsistent column counts
# - Empty rows (if skip_empty=True)
# - Mixed data types
# - Encoding issues
```

## Error Handling

```python
try:
    csv_file = CSVFile("nonexistent.csv")
except FileNotFoundError:
    print("File not found")

try:
    csv_file.update_row(100, {"name": "Test"})  # Invalid index
except IndexError as e:
    print(f"Error: {e}")

try:
    csv_file.filter_by_column("invalid_column", "value")
except KeyError as e:
    print(f"Column error: {e}")
```

## Performance Tips

- Use `filter_*` methods for large datasets instead of manual looping
- Batch operations and call `save()` once at the end
- Use column indexes instead of header names for better performance
- Set `auto_cast=False` if you don't need type conversion

## License

This project is open source and available under the [MIT License](LICENSE).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
