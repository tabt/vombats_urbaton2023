from transformers.utils import send_example_telemetry
from transformers import OwlViTProcessor, OwlViTForObjectDetection
import numpy as np
from PIL import Image
import torch
import matplotlib.pyplot as plt
from transformers.image_utils import ImageFeatureExtractionMixin
from matplotlib.patches import Rectangle
from settings import *


def run_owl(image_original, category):
  # image_original = Image.open(image_path)
  image = Image.fromarray(np.uint8(image_original)).convert("RGB")

  model = OwlViTForObjectDetection.from_pretrained("google/owlvit-base-patch32")
  processor = OwlViTProcessor.from_pretrained("google/owlvit-base-patch32")

  text_queries = OBJECTS_TO_FIND
  device = torch.device("cpu")

  inputs = processor(text=text_queries, images=image, return_tensors="pt").to(device)

  # Print input names and shapes
  for key, val in inputs.items():
      print(f"{key}: {val.shape}")
  
  # Set model in evaluation mode
  model = model.to(device)
  model.eval()

  # Get predictions
  with torch.no_grad():
    outputs = model(**inputs)

  for k, val in outputs.items():
      if k not in {"text_model_output", "vision_model_output"}:
          print(f"{k}: shape of {val.shape}")

  print("\nText model outputs")
  for k, val in outputs.text_model_output.items():
      print(f"{k}: shape of {val.shape}")

  print("\nVision model outputs")
  for k, val in outputs.vision_model_output.items():
      print(f"{k}: shape of {val.shape}")


  mixin = ImageFeatureExtractionMixin()

  # Load example image
  image_size = model.config.vision_config.image_size
  shape_original = image.size
  image = mixin.resize(image, image_size)
  input_image = np.asarray(image).astype(np.float32) / 255.0

  # Threshold to eliminate low probability predictions
  score_threshold = 0.05

  # Get prediction logits
  logits = torch.max(outputs["logits"][0], dim=-1)
  scores = torch.sigmoid(logits.values).cpu().detach().numpy()

  # Get prediction labels and boundary boxes
  labels = logits.indices.cpu().detach().numpy()
  boxes = outputs["pred_boxes"][0].cpu().detach().numpy()

  def plot_predictions(input_image, text_queries, scores, boxes, labels):
      fig, ax = plt.subplots(1, 1, figsize=(8, 8))
      ax.imshow(input_image, extent=(0, 1, 1, 0))
      ax.set_axis_off()

      for score, box, label in zip(scores, boxes, labels):
        if score < score_threshold:
          continue

        cx, cy, w, h = box
        ax.plot([cx-w/2, cx+w/2, cx+w/2, cx-w/2, cx-w/2],
                [cy-h/2, cy-h/2, cy+h/2, cy+h/2, cy-h/2], "r")
        ax.text(
            cx - w / 2,
            cy + h / 2 + 0.015,
            f"{text_queries[label]}: {score:1.2f}",
            ha="left",
            va="top",
            color="red",
            bbox={
                "facecolor": "white",
                "edgecolor": "red",
                "boxstyle": "square,pad=.3"
            })
      plt.savefig('bboxes.png', bbox_inches='tight')
      bboxes = Image.open("bboxes.png")
      bboxes = bboxes.resize(shape_original)
      
      return bboxes
            
  bboxes = plot_predictions(input_image, text_queries, scores, boxes, labels)

  fig, ax = plt.subplots(1, 1, figsize=(8, 8))
  fig.set_facecolor("black")
  ax.imshow(input_image, extent=(0, 1, 1, 0), alpha=0)
  ax.set_axis_off()

  for score, box, label in zip(scores, boxes, labels):
    if score < score_threshold: # or text_queries[label] != category:
      continue

    cx, cy, w, h = box
    ax.add_patch(Rectangle((cx-w/2, cy-h/2), w, h, facecolor = 'white'))
  plt.savefig('mask.png', bbox_inches='tight')

  mask = Image.open("mask.png")
  mask = mask.resize(shape_original)

  image_original.save("photo.png")
  mask.save('mask.png', bbox_inches='tight')
  
  return image_original, mask, bboxes


if __name__ == "__main__":
    run_owl("../images/graf-2.jpg", "graffity")
