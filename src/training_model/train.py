from ultralytics import YOLO

def main():
    # Load a model
    model = YOLO("yolov8n.yaml")  # Build a new model from scratch

    # Use the model
    results = model.train(data="config.yaml", epochs=75)  # Train the model

if __name__ == '__main__':
    main()
