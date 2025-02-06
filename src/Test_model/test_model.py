from ultralytics import YOLO
from pathlib import Path
import os

def test_model(model_path, images_path, output_dir="inference_results"):
    # Load the trained model
    model = YOLO(model_path)
    
    # Create the output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Perform inference on the images in the specified directory
    results = model(images_path, conf=0.55)

    # Loop through the results and save them
    for result in results:
        # Access the image file name from the input image path
        img_file = result.path.split("\\")[-1]  # Extract file name from the path
        
        # Define output image path where results will be saved
        output_img_path = Path(output_dir) / f"result_{img_file}"

        # Save the result using the plot() method
        result.plot(save=True, filename=str(output_img_path))  # Saves the results image
        
        # Optional: Show results for immediate feedback
        # result.show()  # Display the image with bounding boxes and predictions

def main():
    # Define the paths
    model_path = "C:/Users/joshu/runs/detect/train2/weights/best.pt"  # Path to your trained model
    images_path = "C:/Users/joshu/Projects/Senior_Project/test_pictures"  # Path to the folder with images

    # Call the test function
    test_model(model_path, images_path, output_dir="image_results")

# Run the main function
if __name__ == '__main__':
    main()
