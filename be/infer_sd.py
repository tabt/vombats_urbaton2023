from diffusers import StableDiffusionInpaintPipeline
import torch
from PIL import Image

def run_inpaint(image_path, mask_path):
    pipe = StableDiffusionInpaintPipeline.from_pretrained(
        "stabilityai/stable-diffusion-2-inpainting",
        torch_dtype=torch.float32,
    )
    pipe.to("cpu")

    prompt = "the empty wall with color of building on this image"

    img = Image.open(image_path)
    mask = Image.open(mask_path)

    image = pipe(prompt=prompt, image=img, mask_image=mask).images[0]

    image.save('result.png', bbox_inches='tight')

    return image

if __name__ == "__main__":
    run_inpaint("photo.png", "mask.png")