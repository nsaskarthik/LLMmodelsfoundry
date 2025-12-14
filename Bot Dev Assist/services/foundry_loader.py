import time

from foundry_local import FoundryLocalManager

# Start the server and keep it alive
manager = FoundryLocalManager("qwen2.5-coder-7b-instruct-generic-cpu")
manager.load_model("qwen2.5-coder-7b-instruct-generic-cpu")

print(f"\nSERVER RUNNING AT: {manager.service_uri}")
print("Leave this window open!")

# Keep script running
while True:
    time.sleep(1)
