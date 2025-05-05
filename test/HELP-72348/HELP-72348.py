import json
import time
from bson import encode, decode

# Number of repetitions
x = 1

# Load JSON from a file
with open("HELP-72348.json") as f:
    data = json.load(f)

start = time.perf_counter()
for _ in range(x):
    print(f"Running iteration {_ + 1} of {x}...")
    bson_data = encode(data)
    decoded_data = decode(bson_data)

end = time.perf_counter()

print(f"Time taken for {x} iterations: {end - start:.2f} seconds")
