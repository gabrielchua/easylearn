import base64
import io
import random
from PIL import Image

import pandas as pd
import requests
import streamlit as st

SD_ENDPOINT = "http://stable-diffusion-hackathon.5165809643129598.ap-southeast-1.pai-eas.aliyuncs.com/sdapi/v1/txt2img"
QWEN_ENDPOINT = "http://qwen-hackathon.5165809643129598.ap-southeast-1.pai-eas.aliyuncs.com/"

df = pd.read_csv("sample_qns.csv")

def generate_question_system_prompt():
    """
    Call the Qwen API to generate a system prompt for a question
    """
    random_row = df.sample(1)
    # st.write(random_row)
    question = random_row["question"]
    option1 = random_row["option1"]
    option2 = random_row["option2"]
    option3 = random_row["option3"]
    option4 = random_row["option4"]
    answer = random_row["answer"]


    PROMPT = """
    You are a 4th grade {topic} teacher.

    Your task is to generate Multiple Choice Questions (MCQs) for your students.
    Include 4 options, and indicate which is correct.

    You must ONLY reply in valid json. 

    For example 

    {
        \"QN\": {question}, 
        \"CHOICES"\: {
            \"1\": {option1}, 
            \"2\": {option2},
            \"3\": {option3},
            \"4\": {option4}
            }
        \"Ans\": {answer}
    }

    The question should be about {topic}

    """

    return PROMPT

def generate_img_system_prompt(topic):
    """
    Call the Qwen API to generate a system prompt for a image
    """
    GENERATE_IMG_DESC = f"""
    You are an expert comic artist.

    Generate a description for an image about {topic}

    The description MUST be cute and child-friendly, and found in a children's textbook.

    The description MUST be at most 100 characters long.

    """

    return GENERATE_IMG_DESC


def text_to_img(topic):
    """
    Call the Stable Diffusion API to convert text to an image
    """

    img_caption = _chat_completion(generate_img_system_prompt(topic), 
                                   f"Generate the image about {topic}")


    headers = {
        "Content-Type": "application/json",
        "Authorization": st.secrets["SD_API_KEY"]
    
    }
    data = {
        "prompt": img_caption,
        "steps": 20
    }
    response = requests.post(SD_ENDPOINT, json=data, headers=headers)
    results = response.json()
    image_str = results["images"][0]
    image = _decode_base64_image(image_str)
    return image

# Function to decode base64 and return a PIL image
def _decode_base64_image(base64_string):
    # Decode the Base64 string, making sure to remove the "data:image/png;base64," part if present
    if ";base64," in base64_string:
        _, base64_string = base64_string.split(";base64,")
    decoded_image = base64.b64decode(base64_string)
    # Convert binary data to PIL Image
    image = Image.open(io.BytesIO(decoded_image))
    return image

def generate_qn():
    """
    Call the Qwen API to generate a question
    """
    return _chat_completion(generate_question_system_prompt(), random.choice(["science", "geography"]))
    
def _chat_completion(system_prompt, prompt):
    """
    Call the Qwen API to get a chat completion
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": st.secrets["QWEN_API_KEY"]
    }
    data = {
        "system_prompt": system_prompt,
        "prompt": prompt
    }

    response = requests.post(QWEN_ENDPOINT, json=data, headers=headers)
    result = response.json()
    return result["response"]