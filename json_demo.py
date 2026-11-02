import json

chat_history = [
    {"role": "user",
     "content": "My name is Siva"},
    {"role": "assistant",
     "content": "Hello Siva. How can I help you?"} 
]

# Create the file and write the json format into it
with open("json_demo_file.json", "w") as file:
    json.dump(chat_history, file,indent=4)


with open("json_demo_file.json", "r") as file:
    data = json.load(file)

    print(data)