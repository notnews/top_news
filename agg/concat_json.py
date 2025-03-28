import os
import json

def dedupe_list_of_dicts(items):
    seen = set()
    deduped = []
    for item in items:
        key = json.dumps(item, sort_keys=True)
        if key not in seen:
            seen.add(key)
            deduped.append(item)
    return deduped

def load_and_concat_jsons(dir_path):
    data = []
    for filename in os.listdir(dir_path):
        if filename.endswith(".json"):
            full_path = os.path.join(dir_path, filename)
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = json.load(f)
                    if isinstance(content, list):
                        deduped = dedupe_list_of_dicts(content)
                        data.extend(deduped)
                    else:
                        data.append(content)
            except Exception as e:
                print(f"⚠️ Skipping {filename}: {e}")
    return data

if __name__ == "__main__":
    dir_path = "./"
    all_data = load_and_concat_jsons(dir_path)

    with open("agg.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2)

    print(f"✅ Saved {len(all_data)} unique items to agg.json")


