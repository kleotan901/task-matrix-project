import csv
import os
from datetime import datetime
from io import StringIO


def to_csv_content(data):
    """
    Generate CSV content as a string from the provided data dictionary.
    The to_csv_content function generates the CSV content in memory using StringIO,
    avoiding the need to create and delete a temporary file.
    """
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=data.keys())
    writer.writeheader()
    writer.writerow(data)
    return output.getvalue()
