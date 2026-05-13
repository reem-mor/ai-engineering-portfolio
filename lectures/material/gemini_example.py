from google import genai

client = genai.Client(api_key="AIzaSyD2fyni9M_m9wzYLODr2drek-s_t-C49xA")

response = client.models.generate_content(
    model="gemini-3.1-pro-preview",
    contents="What is the capital of France?",

)

print(response.text)

