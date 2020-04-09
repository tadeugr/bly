import json
import uuid 
import sys

# Convert boolean values to string
def convert(obj):
    if isinstance(obj, bool):
        return str(obj).lower()
    if isinstance(obj, (list, tuple)):
        return [convert(item) for item in obj]
    if isinstance(obj, dict):
        return {convert(key):convert(value) for key, value in obj.items()}
    return obj


with open(sys.argv[1]) as json_file:
    data = json.load(json_file)
    for item in data:
        item["_bly_uuid"] = str(uuid.uuid1())

data_str = json.dumps(convert(data))
print(data_str)
sys.exit()
with open('data.json', 'w') as outfile:
    json.dump(data, outfile)
