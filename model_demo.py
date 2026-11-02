from openai import OpenAI

client = OpenAI()

input_messages = [
    {"role": "user", "content": "The project code is amber fox."},
    {"role": "assistant", "content": "Understood—the project code is amber fox."},
    {"role": "user", "content": "What is the project code?"},
]

response = client.responses.create(
    model="gpt-4.1-mini",
    input=input_messages,
)

print(response.output_text)
assert response.usage is not None
print(response.usage.input_tokens)
print(response.usage.output_tokens)
print(response.usage.total_tokens)

response = client.responses.create(
    model="gpt-4.1-mini",
    input='what is the project code?',
)

print(response.output_text)
assert response.usage is not None
print(response.usage.input_tokens)
print(response.usage.output_tokens)
print(response.usage.total_tokens)