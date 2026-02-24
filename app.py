# ==============================================================================
# YOLOv5 Vehicle Detection — Process video and annotate with bounding boxes
# ==============================================================================

import os
import sys
import cv2
import torch

# ── Configuration ────────────────────────────────────────────────────────────
VIDEO_DIR = "vids"
INPUT_VIDEO  = os.path.join(VIDEO_DIR, "20250209_163940.mp4")
OUTPUT_VIDEO = os.path.join(VIDEO_DIR, "output_detected.mp4")


def main():
    # ── Load YOLOv5 model ────────────────────────────────────────────────
    print("Loading YOLOv5 model...")
    try:
        model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
    except Exception as exc:
        print(f"Error loading model: {exc}")
        sys.exit(1)

    # ── Open video ───────────────────────────────────────────────────────
    if not os.path.exists(INPUT_VIDEO):
        print(f"Error: Input video not found: {INPUT_VIDEO}")
        sys.exit(1)

    cap = cv2.VideoCapture(INPUT_VIDEO)
    if not cap.isOpened():
        print(f"Error: Could not open video: {INPUT_VIDEO}")
        sys.exit(1)

    frame_width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps          = int(cap.get(cv2.CAP_PROP_FPS)) or 30
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"Input : {INPUT_VIDEO}")
    print(f"Size  : {frame_width}x{frame_height} @ {fps} fps ({total_frames} frames)")

    # ── Video writer ─────────────────────────────────────────────────────
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(OUTPUT_VIDEO, fourcc, fps, (frame_width, frame_height))
    if not out.isOpened():
        print(f"Error: Could not create output video: {OUTPUT_VIDEO}")
        cap.release()
        sys.exit(1)

    # ── Process frames ───────────────────────────────────────────────────
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # YOLOv5 inference
        results = model(frame)

        # Get detections as DataFrame
        df = results.pandas().xyxy[0]
        vehicle_count = len(df)

        # Draw bounding boxes and labels
        for _, row in df.iterrows():
            x1 = int(row['xmin'])
            y1 = int(row['ymin'])
            x2 = int(row['xmax'])
            y2 = int(row['ymax'])
            conf = row['confidence']
            cls_name = row['name']  # YOLOv5 pandas output has 'name' column

            label = f"{cls_name} {conf:.2f}"
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Display vehicle count overlay
        cv2.putText(frame, f"Vehicles: {vehicle_count}", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

        out.write(frame)
        frame_count += 1

        # Progress every 100 frames
        if frame_count % 100 == 0:
            pct = (frame_count / total_frames * 100) if total_frames > 0 else 0
            print(f"  Frame {frame_count}/{total_frames} ({pct:.1f}%) — "
                  f"{vehicle_count} vehicles detected")

    # ── Cleanup ──────────────────────────────────────────────────────────
    cap.release()
    out.release()
    cv2.destroyAllWindows()

    print(f"\nDone! Processed {frame_count} frames.")
    print(f"Output saved: {OUTPUT_VIDEO}")


if __name__ == "__main__":
    main()
