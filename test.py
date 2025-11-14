import json
response = f"""
{{
  "title": "NVIDIA 5090 - The Most Powerful GeForce GPU Ever Made!",
  "description": "The NVIDIA® GeForce RTX™ 5090 is the most powerful GeForce GPU ever made, bringing game-changing capabilities to gamers and creators.",
  "keywords": [
    "Game with Ray Tracing",
    "Lowest Latency",
    "AI Horsepower"
  ]
}}

"""
jsonResponse = json.loads(response)

final = {}
tempKeys = list(jsonResponse.keys())
final["title"] = jsonResponse[tempKeys[0]]
final["description"] = jsonResponse[tempKeys[1]]
final["keywords"] = jsonResponse[tempKeys[2]]

print(final)