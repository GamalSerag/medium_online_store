
import urllib.request
from urllib.error import HTTPError, URLError

output_file = 'error_trace.log'

try:
    with open(output_file, 'w', encoding='utf-8') as f:
        try:
            with urllib.request.urlopen('http://127.0.0.1:8000/admin-dashboard/') as response:
                f.write("Success\n")
                f.write(response.read().decode())
        except HTTPError as e:
            f.write(f"HTTP Error {e.code}:\n")
            f.write(e.read().decode())
        except URLError as e:
            f.write(f"URL Error: {e.reason}\n")
        except Exception as e:
            f.write(f"Error: {e}\n")
    print(f"Output written to {output_file}")
except Exception as e:
    print(f"Failed: {e}")
