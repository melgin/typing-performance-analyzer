from pathlib import Path
import csv
import json

class FileReader:

    @staticmethod
    def read_csv_file(file_name:str) -> set[str]:
        """
        Reads a single-column CSV file and returns a set of values
        for fastest exact-match lookup.
        """

        # Get the directory where this Python file lives
        base_dir = Path(__file__).resolve().parent

        # Build path to the CSV file
        file_path = base_dir / "resources" / file_name

        with open(file_path, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            return {row[0].strip() for row in reader if row}

    @staticmethod
    def read_json_file(folder:str, file_name:str) -> dict[str, list[str]]:
        # Get the directory where this Python file lives
        base_dir = Path(__file__).resolve().parent

        # Build path to the CSV file
        file_path = base_dir / folder / file_name

        data = {}
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
