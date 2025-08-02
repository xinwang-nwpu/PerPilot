import base64
from openai import OpenAI, APIConnectionError, APIError


def append_to_file(id, content):
    with open(f"log/log{id}.txt", 'a', encoding='utf-8') as file:
        file.write(content + '\n') 

def inference_chat(chat, model, api_url, token):
    client = OpenAI(
        api_key=token,
        base_url=api_url
    )

    messages = [{"role": role, "content": content} for role, content in chat]

    while True:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=4096,
                temperature=0.0,
                seed=1234

            )
            return response.choices[0].message.content
        except APIConnectionError as e:
            print(f"Network Error: {e}")
        except APIError as e:
            print(f"API Error: {e}")
            if e.response:
                try:
                    print(e.response.json())
                except:
                    print("Could not parse error response")
            if e.status_code >= 500:
                continue
            else:
                raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            continue
        else:
            break
