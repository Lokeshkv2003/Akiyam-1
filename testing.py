##Run this dependencies in terminal before executing the whole code
'''
pip install openai==0.28
pip install open3d transformers pillow imageio
pip install git+https://github.com/openai/shap-e.git
git clone https://github.com/openai/shap-e.git
cd shap-e
pip install -e .
cd ..
python --version
pip install open3d
'''

# packages
import os
import openai
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from tkinter import Tk, filedialog  # For file explorer

# Set your Groq API key
os.environ["GROQ_API_KEY"] = "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"

#Get user input
def get_user_input():
    mode = input("Enter 'text' to provide prompt or 'image' to upload an image: ").strip().lower()

    if mode == 'text':
        prompt = input("Enter your text prompt for the 3D model: ")
        return {"type": "text", "data": prompt}

    elif mode == 'image':
        # Open file explorer to pick image
        Tk().withdraw()  # Hide Tkinter root window
        image_path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.webp;*.bmp")]
        )
        if not image_path:
            print("No file selected. Exiting.")
            exit(1)

        try:
            img = Image.open(image_path)
            img.show()
            return {"type": "image", "data": img}
        except Exception as e:
            print(f" Error loading image: {e}")
            exit(1)

    else:
        raise ValueError("Please type 'text' or 'image'.")

#Extract context
def context_agent(input_data):
    if input_data["type"] == "text":
        print("Text input detected.")
        print(f"> Prompt: {input_data['data']}")
        return input_data["data"]

    elif input_data["type"] == "image":
        print("Image input detected. Generating caption...")
        processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
        inputs = processor(images=input_data["data"], return_tensors="pt")
        caption_ids = model.generate(**inputs)
        caption = processor.decode(caption_ids[0], skip_special_tokens=True)
        print(f"Extracted Caption: {caption}")
        return caption

#Generate Blender code
def generate_blender_code(prompt):
    print("Sending prompt to Groq's LLaMA for Blender Python code generation...")
    openai.api_key = os.getenv("GROQ_API_KEY")
    openai.api_base = "https://api.groq.com/openai/v1"

    response = openai.ChatCompletion.create(
        model="llama-3-groq-70b-tool-use-preview",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a highly skilled Python developer specializing in Blender bpy scripting. "
                    "Your task is to generate only executable Blender Python code based on the given prompt. "
                    "Do not include explanations, comments, or extra text—only valid Python code. "
                    "Ensure the script saves the model as output.blend or exports it as .obj/.fbx."
                )
            },
            {
                "role": "user",
                "content": f"{prompt}"
            }
        ]
    )

    code = response["choices"][0]["message"]["content"]
    print("Blender Python code generated.")

    with open("run_agent.py", "w", encoding="utf-8") as f:
        f.write(code)

#Run Blender script
def run_execution_agent():
    print("Running Blender to generate the 3D model...")
    blender_path = r'"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe"'
    os.system(f'{blender_path} --background --python run_agent.py')

#Show final message
def show_3d_output():
    print("3D model created! Open 'output.blend' or exported file in Blender to view it.")

#Full flow
if __name__ == "__main__":
    user_input = get_user_input()
    context = context_agent(user_input)
    generate_blender_code(context)
    run_execution_agent()
    show_3d_output()















