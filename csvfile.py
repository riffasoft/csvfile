import csv
from collections import Counter
from typing import Callable, Any


class CSVFile:
    def __init__(self, path, candidates=None, has_header=True,
                 skip_empty=True, auto_cast=True, normalize_header=True):
        
        if candidates is None:
            candidates = [",", ";", "|", "\t"]  # Default delimiters

        self.path = path
        self.candidates = candidates
        self.has_header = has_header
        self.skip_empty = skip_empty
        self.auto_cast = auto_cast
        self.normalize_header = normalize_header

        self.encoding = None
        self.delimiter = None
        self.header = []
        self.rows = []
        self._load_file()

    # ---------- Utility ----------
    def _auto_cast(self, value: str):
        if value is None:
            return None
        v = value.strip()
        if v == "":
            return ""
        # Int
        if v.isdigit() or (v.startswith("-") and v[1:].isdigit()):
            try:
                return int(v)
            except Exception:
                pass
        # Float
        try:
            return float(v)
        except ValueError:
            pass
        # Bool
        lower_v = v.lower()
        if lower_v in ("true", "false"):
            return lower_v == "true"
        return v

    def _normalize_header(self, headers):
        return [h.strip().lower().replace(" ", "_").replace("-", "_") for h in headers]

    def _detect_encoding(self, encodings=("utf-8", "utf-8-sig", "latin-1")):
        for enc in encodings:
            try:
                with open(self.path, "r", encoding=enc) as f:
                    content = f.read().splitlines()
                return enc, content
            except UnicodeDecodeError:
                continue
        # PERUBAHAN DI SINI: ganti "CSVData" menjadi "CSVFile"
        raise UnicodeDecodeError("CSVFile", self.path, 0, 0, "Tidak bisa decode file dengan encoding fallback")

    def _detect_delimiter(self, sample_lines):
        scores = {}
        for delim in self.candidates:
            try:
                reader = csv.reader(sample_lines, delimiter=delim, quotechar='"')
                lengths = [len(row) for row in reader if row]
                if not lengths:
                    continue
                common_len, freq = Counter(lengths).most_common(1)[0]
                scores[delim] = freq
            except Exception:
                continue
        return max(scores, key=scores.get) if scores else ","

    # ---------- Load file ----------
    def _load_file(self):
        self.encoding, file_content = self._detect_encoding()
        self.delimiter = self._detect_delimiter(file_content)

        with open(self.path, "r", encoding=self.encoding) as f:
            reader = csv.reader(f, delimiter=self.delimiter, quotechar='"')
            rows = [row for row in reader if (not self.skip_empty or any(cell.strip() for cell in row))]

        if self.has_header and rows:
            self.header, self.rows = rows[0], rows[1:]
            if self.normalize_header:
                self.header = self._normalize_header(self.header)
            if self.auto_cast:
                self.rows = [[self._auto_cast(v) for v in row] for row in self.rows]
        else:
            self.rows = [[self._auto_cast(v) for v in row] for row in rows] if self.auto_cast else rows

    def _get_expected_columns_count(self):
        """Mendapatkan jumlah kolom yang diharapkan"""
        if self.has_header:
            return len(self.header)
        elif self.rows:
            return len(self.rows[0])
        else:
            return 0

    def _adjust_columns(self, data, expected_columns):
        """
        Menyesuaikan jumlah kolom data dengan yang diharapkan.
        - Jika data kurang: tambahkan field kosong
        - Jika data lebih: potong sesuai jumlah kolom
        """
        if len(data) < expected_columns:
            # Tambahkan field kosong jika kurang
            return data + [""] * (expected_columns - len(data))
        elif len(data) > expected_columns:
            # Potong jika lebih
            return data[:expected_columns]
        else:
            # Sudah pas
            return data

    def _get_column_index(self, col_identifier):
        """Mendapatkan index kolom dari identifier (string nama header atau int index)"""
        if isinstance(col_identifier, str):
            if not self.has_header:
                raise ValueError("Tidak bisa menggunakan nama header karena CSV tidak punya header")
            if col_identifier not in self.header:
                raise KeyError(f"Header '{col_identifier}' tidak ditemukan")
            return self.header.index(col_identifier)
        elif isinstance(col_identifier, int):
            return col_identifier
        else:
            raise TypeError("col_identifier harus string (nama header) atau int (index kolom)")

    # ---------- Filter Methods ----------
    def filter_rows(self, condition: Callable[[list, int], bool]) -> 'CSVFile':
        """
        Filter baris berdasarkan fungsi condition.
        Fungsi condition menerima parameter (row, index) dan return boolean.
        
        Args:
            condition: Fungsi yang menerima (row, index) dan return True/False
        
        Returns:
            CSVFile baru dengan baris yang memenuhi kondisi
        """
        filtered_rows = [row for i, row in enumerate(self.rows) if condition(row, i)]
        
        # PERUBAHAN DI SINI: ganti CSVFile.__new__(CSVFile)
        filtered_csv = CSVFile.__new__(CSVFile)
        filtered_csv.path = self.path
        filtered_csv.candidates = self.candidates
        filtered_csv.has_header = self.has_header
        filtered_csv.skip_empty = self.skip_empty
        filtered_csv.auto_cast = self.auto_cast
        filtered_csv.normalize_header = self.normalize_header
        filtered_csv.encoding = self.encoding
        filtered_csv.delimiter = self.delimiter
        filtered_csv.header = self.header[:]
        filtered_csv.rows = filtered_rows
        
        return filtered_csv

    def filter_by_column(self, col_identifier, value: Any, operator: str = "==") -> 'CSVFile':
        """
        Filter baris berdasarkan nilai kolom tertentu.
        
        Args:
            col_identifier: Nama header (str) atau index kolom (int)
            value: Nilai yang dicari
            operator: Operator perbandingan ("==", "!=", ">", "<", ">=", "<=", "in", "not in", "contains")
        
        Returns:
            CSVFile baru dengan baris yang memenuhi kondisi
        """
        col_index = self._get_column_index(col_identifier)
        
        def condition(row, index):
            if col_index >= len(row):
                return False
            
            cell_value = row[col_index]
            
            if operator == "==":
                return cell_value == value
            elif operator == "!=":
                return cell_value != value
            elif operator == ">":
                return cell_value > value
            elif operator == "<":
                return cell_value < value
            elif operator == ">=":
                return cell_value >= value
            elif operator == "<=":
                return cell_value <= value
            elif operator == "in":
                return cell_value in value
            elif operator == "not in":
                return cell_value not in value
            elif operator == "contains":
                return value in str(cell_value)
            elif operator == "startswith":
                return str(cell_value).startswith(str(value))
            elif operator == "endswith":
                return str(cell_value).endswith(str(value))
            else:
                raise ValueError(f"Operator '{operator}' tidak didukung")
        
        return self.filter_rows(condition)

    def filter_empty(self, col_identifier=None) -> 'CSVFile':
        """
        Filter baris yang kosong atau baris dengan kolom tertentu yang kosong.
        
        Args:
            col_identifier: Jika None, filter baris yang benar-benar kosong.
                          Jika diberikan, filter baris dengan kolom tertentu yang kosong.
        
        Returns:
            CSVFile baru dengan baris yang tidak kosong
        """
        if col_identifier is None:
            # Filter baris yang tidak kosong sama sekali
            def condition(row, index):
                return any(cell != "" and cell is not None for cell in row)
        else:
            # Filter baris dengan kolom tertentu yang tidak kosong
            col_index = self._get_column_index(col_identifier)
            def condition(row, index):
                if col_index < len(row):
                    return row[col_index] != "" and row[col_index] is not None
                return False
        
        return self.filter_rows(condition)

    def filter_multiple(self, conditions: list) -> 'CSVFile':
        """
        Filter baris dengan multiple conditions (AND logic).
        
        Args:
            conditions: List of tuples (col_identifier, value, operator) atau 
                       list of callable conditions
        
        Returns:
            CSVFile baru dengan baris yang memenuhi semua kondisi
        """
        def combined_condition(row, index):
            for cond in conditions:
                if callable(cond):
                    # Condition adalah fungsi
                    if not cond(row, index):
                        return False
                else:
                    # Condition adalah tuple (col_identifier, value, operator)
                    col_id, value, operator = cond
                    col_index = self._get_column_index(col_id)
                    
                    if col_index >= len(row):
                        return False
                    
                    cell_value = row[col_index]
                    
                    if operator == "==":
                        if cell_value != value:
                            return False
                    elif operator == "!=":
                        if cell_value == value:
                            return False
                    elif operator == ">":
                        if not (cell_value > value):
                            return False
                    elif operator == "<":
                        if not (cell_value < value):
                            return False
                    elif operator == ">=":
                        if not (cell_value >= value):
                            return False
                    elif operator == "<=":
                        if not (cell_value <= value):
                            return False
                    elif operator == "in":
                        if cell_value not in value:
                            return False
                    elif operator == "not in":
                        if cell_value in value:
                            return False
                    elif operator == "contains":
                        if value not in str(cell_value):
                            return False
            return True
        
        return self.filter_rows(combined_condition)

    def get_rows_with_indices(self, condition: Callable[[list, int], bool]) -> list:
        """
        Mendapatkan baris beserta index aslinya yang memenuhi kondisi.
        
        Returns:
            List of tuples (index_asli, row)
        """
        return [(i, row) for i, row in enumerate(self.rows) if condition(row, i)]

    # ---------- Public Methods ----------
    def to_dict(self):
        """Return list of dict (jika ada header)."""
        if not self.has_header or not self.header:
            raise ValueError("CSV tidak punya header, gunakan rows langsung.")
        return [dict(zip(self.header, row)) for row in self.rows]

    def update_row(self, index, new_data):
        """
        Update baris berdasarkan index.
        - new_data bisa dict (berdasarkan nama header) atau list (berdasarkan urutan kolom)
        - atau dict dengan key int (berdasarkan index kolom)
        """
        if index < 0 or index >= len(self.rows):
            raise IndexError(f"Index baris {index} tidak valid. Jumlah baris: {len(self.rows)}")

        expected_columns = self._get_expected_columns_count()
        
        if self.has_header and isinstance(new_data, dict):
            # Cek jika dict berisi key int (index kolom) atau string (nama header)
            has_int_keys = any(isinstance(k, int) for k in new_data.keys())
            has_str_keys = any(isinstance(k, str) for k in new_data.keys())
            
            if has_int_keys and has_str_keys:
                raise ValueError("Dict tidak boleh campuran int (index) dan string (header)")
            
            if has_int_keys:
                # Update berdasarkan index kolom
                updated_row = self.rows[index][:]
                for col_index, value in new_data.items():
                    if 0 <= col_index < len(updated_row):
                        updated_row[col_index] = value
                    else:
                        # Jika index kolom melebihi, extend row
                        if col_index >= len(updated_row):
                            updated_row.extend([""] * (col_index - len(updated_row) + 1))
                        updated_row[col_index] = value
                # Sesuaikan dengan jumlah kolom yang diharapkan
                updated_row = self._adjust_columns(updated_row, expected_columns)
                self.rows[index] = updated_row
            else:
                # Update berdasarkan nama header
                updated_row = self.rows[index][:]
                for col_name, value in new_data.items():
                    if col_name in self.header:
                        col_index = self.header.index(col_name)
                        updated_row[col_index] = value
                    else:
                        # Jika header tidak ditemukan, abaikan atau tambahkan kolom baru?
                        print(f"Peringatan: Header '{col_name}' tidak ditemukan, diabaikan")
                self.rows[index] = updated_row
                
        elif isinstance(new_data, list):
            # Update berdasarkan urutan kolom
            adjusted_data = self._adjust_columns(new_data, expected_columns)
            self.rows[index] = adjusted_data
        else:
            raise TypeError("new_data harus dict (dengan key int/string) atau list")

    def update_cell(self, row_index, col_identifier, value):
        """
        Update satu sel tertentu.
        - col_identifier bisa string (nama header) atau int (index kolom)
        """
        if row_index < 0 or row_index >= len(self.rows):
            raise IndexError("Index baris tidak valid")
        
        if isinstance(col_identifier, str):
            if not self.has_header:
                raise ValueError("Tidak bisa menggunakan nama header karena CSV tidak punya header")
            if col_identifier not in self.header:
                raise KeyError(f"Header '{col_identifier}' tidak ditemukan")
            col_index = self.header.index(col_identifier)
        elif isinstance(col_identifier, int):
            col_index = col_identifier
            expected_columns = self._get_expected_columns_count()
            if col_index >= expected_columns:
                # Extend row jika index kolom melebihi
                self.rows[row_index].extend([""] * (col_index - len(self.rows[row_index]) + 1))
                # Sesuaikan kembali dengan jumlah kolom yang diharapkan
                self.rows[row_index] = self._adjust_columns(self.rows[row_index], expected_columns)
        else:
            raise TypeError("col_identifier harus string (nama header) atau int (index kolom)")
        
        self.rows[row_index][col_index] = value

    def save(self, path=None):
        """
        Simpan data ke file CSV.
        - Jika path tidak diberikan, akan menimpa file asli.
        - Jika path diberikan, akan menyimpan ke file baru.
        """
        save_path = path or self.path
        
        # Pastikan semua row memiliki jumlah kolom yang konsisten
        expected_columns = self._get_expected_columns_count()
        adjusted_rows = [self._adjust_columns(row, expected_columns) for row in self.rows]
        
        # Prepare data untuk disimpan
        if self.has_header:
            data_to_save = [self.header] + adjusted_rows
        else:
            data_to_save = adjusted_rows
        
        # Convert data ke string jika diperlukan (karena auto_cast mungkin mengubah tipe data)
        data_to_save = [[str(cell) if cell is not None else "" for cell in row] for row in data_to_save]
        
        with open(save_path, "w", encoding=self.encoding, newline='') as f:
            writer = csv.writer(f, delimiter=self.delimiter, quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerows(data_to_save)
        
        print(f"Data berhasil disimpan ke: {save_path}")

    def update_row_and_save(self, index, new_data, path=None):
        """
        Update baris dan langsung simpan ke file.
        - Jika path tidak diberikan, akan menimpa file asli.
        - Jika path diberikan, akan menyimpan ke file baru.
        """
        self.update_row(index, new_data)
        self.save(path)

    def update_cell_and_save(self, row_index, col_identifier, value, path=None):
        """
        Update satu sel dan langsung simpan ke file.
        """
        self.update_cell(row_index, col_identifier, value)
        self.save(path)

    def add_row(self, new_data):
        """
        Tambah baris baru.
        - new_data bisa dict (berdasarkan nama header/index) atau list (berdasarkan urutan kolom)
        """
        expected_columns = self._get_expected_columns_count()
        
        if self.has_header and isinstance(new_data, dict):
            # Cek tipe key
            has_int_keys = any(isinstance(k, int) for k in new_data.keys())
            has_str_keys = any(isinstance(k, str) for k in new_data.keys())
            
            if has_int_keys and has_str_keys:
                raise ValueError("Dict tidak boleh campuran int (index) dan string (header)")
            
            if has_int_keys:
                # Buat baris kosong lalu isi berdasarkan index
                new_row = [""] * expected_columns
                for col_index, value in new_data.items():
                    if col_index >= len(new_row):
                        # Extend jika index melebihi
                        new_row.extend([""] * (col_index - len(new_row) + 1))
                    new_row[col_index] = value
                # Sesuaikan dengan jumlah kolom yang diharapkan
                new_row = self._adjust_columns(new_row, expected_columns)
            else:
                # Buat baris berdasarkan nama header
                new_row = [new_data.get(col, "") for col in self.header]
                
            self.rows.append(new_row)
            
        elif isinstance(new_data, list):
            # Tambah baris berdasarkan urutan kolom
            adjusted_data = self._adjust_columns(new_data, expected_columns)
            self.rows.append(adjusted_data)
        else:
            raise TypeError("new_data harus dict (dengan key int/string) atau list")

    def add_row_and_save(self, new_data, path=None):
        """
        Tambah baris baru dan langsung simpan ke file.
        """
        self.add_row(new_data)
        self.save(path)

    def delete_row(self, index):
        """
        Hapus baris berdasarkan index.
        """
        if 0 <= index < len(self.rows):
            del self.rows[index]
        else:
            raise IndexError("Index baris tidak valid")

    def delete_row_and_save(self, index, path=None):
        """
        Hapus baris dan langsung simpan ke file.
        """
        self.delete_row(index)
        self.save(path)

    def get_columns_count(self):
        """Mendapatkan jumlah kolom"""
        return self._get_expected_columns_count()

    def __repr__(self):
        return f"<CSVFile path={self.path}, rows={len(self.rows)}, columns={self._get_expected_columns_count()}, delimiter='{self.delimiter}'>"
