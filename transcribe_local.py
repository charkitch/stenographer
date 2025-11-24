
import os
import sys
import json
import requests

API_URL = "http://localhost:8000/transcribe"
OUTPUT_DIR = "outputs"

"""Python script to mirror this curl, and 
  
  curl -X POST "http://localhost:8000/transcribe" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@{our movie path}" \
  | jq .
  
  Usage: python3 transcribe_local.py ~/Movies/hello_world.mov
"""


API_URL = "http://localhost:8000/transcribe"
OUTPUT_DIR = "outputs"


def main():
    if len(sys.argv) < 2:
        print("Usage: python transcribe_local.py <path-to-video>")
        sys.exit(1)

    input_path = sys.argv[1]

    if not os.path.isfile(input_path):
        print(f"❌ Error: File not found: {input_path}")
        sys.exit(1)

    # Ensure outputs directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Build output JSON filename
    base = os.path.basename(input_path)
    name_no_ext = os.path.splitext(base)[0]
    output_path = os.path.join(OUTPUT_DIR, f"{name_no_ext}.json")

    print(f"📤 Sending file to whisper API: {input_path}")
    print(f"📥 Will save full JSON to: {output_path}")

    # Send file
    with open(input_path, "rb") as f:
        files = {"file": (base, f, "application/octet-stream")}
        try:
            response = requests.post(API_URL, files=files)
        except Exception as e:
            print(f"❌ Request failed: {e}")
            sys.exit(1)

    if response.status_code != 200:
        print(f"❌ Server error {response.status_code}:\n{response.text}")
        sys.exit(1)

    data = response.json()

    with open(output_path, "w", encoding="utf-8") as out:
        json.dump(data, out, indent=2, ensure_ascii=False)

    print("✅ Done!")
    print(f"📄 Full JSON transcript saved at:")
    print(f"   {output_path}")


if __name__ == "__main__":
    main()
