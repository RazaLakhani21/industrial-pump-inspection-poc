import boto3
import json

#Create Bedrock Runtime Client
bedrock = boto3.client(
    service_name = "bedrock-runtime",
    region_name = "us-east-2"
)

MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"

def generate_bedrock_report(comparison_json):
    structured_data = json.dumps(comparison_json, indent=2)
    
    prompt = f"""
        You are a senior industrial inspection engineer.

        Below is structured before-after inspection data in JSON format:

        {structured_data}

        Generate a professional inspection report.

        Requirements:
        - Max 650 words
        - Mention rust change clearly
        - Mention affected zones
        - State overall condition (Improved / Degraded / Stable)
        - Include risk level (Low / Medium / High)
        - Provide maintenance recommendation
        - Do NOT invent values
        - Be concise and factual
        """

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 500,
        "temperature": 0.2,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps(body)
    )

    result = json.loads(response["body"].read())
    return result["content"][0]["text"]

# import boto3

# b = boto3.client("bedrock-runtime", region_name="ap-south-1")
# print(b)


# import boto3
# import json

# bedrock = boto3.client(
#     service_name="bedrock-runtime",
#     region_name="ap-south-1"
# )

# MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"

# def test_call():
#     prompt = "Write a short industrial inspection summary in 3 lines."

#     body = {
#         "anthropic_version": "bedrock-2023-05-31",
#         "max_tokens": 300,
#         "messages": [
#             {
#                 "role": "user",
#                 "content": prompt
#             }
#         ]
#     }

#     response = bedrock.invoke_model(
#         modelId=MODEL_ID,
#         body=json.dumps(body),
#         contentType="application/json"
#     )

#     result = json.loads(response["body"].read())

#     print(result["content"][0]["text"])


# if __name__ == "__main__":
#     test_call()
