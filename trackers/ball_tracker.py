from ultralytics import YOLO
import numpy as np
import supervision as sv
import pandas as pd
import os
import sys
sys.path.append("../")
from utils import read_stub, save_stub

class BallTracker:
    def __init__(self, model_path):
       self.model =  YOLO(model_path)
       

    def detect_frames(self, frames):
        batch_size =20
        detections=[]
        for i in range(0, len(frames),batch_size):
            batch_frames=frames[i:i+batch_size]
            batch_detections=self.model.predict(batch_frames,conf=0.5)
            detections.extend(batch_detections)

        return detections
    
    def get_object_tracks(self,frames,read_from_stub=False, stub_path=None): #stub stores the already runned/processses sample output to reduce time
        
        if read_from_stub and stub_path and os.path.exists(stub_path):
            tracks = read_stub(read_from_stub,stub_path)
            if tracks is not None:
                if len(tracks) == len(frames):
                    return tracks
        
        print("Running tracking computation...") 
        detections = self.detect_frames(frames)
        tracks = []

        for frame_num,detection in enumerate(detections):
            cls_names=detection.names
            cls_names_inv={v:k for k,v in cls_names.items()}

            detection_supervision = sv.Detections.from_ultralytics(detection)
            tracks.append({})
            chosen_bbox= None
            max_confidence=0

            for frame_detection in detection_supervision:
                bbox= frame_detection[0].tolist()
                cls_id= frame_detection[3]
                confidence= frame_detection[2]

                if cls_id == cls_names_inv["Ball"]:
                    if max_confidence<confidence:
                        chosen_bbox=bbox
                        max_confidence=confidence
            
            if chosen_bbox is not None:
                tracks[frame_num][1]= {"bbox":chosen_bbox}

        if stub_path:
            save_stub(stub_path, tracks)

        return tracks
    
    def remove_wrong_detection(self,ball_positions):

        maximum_allowed_distance = 25
        last_good_frame_index=-1

        for i in range(len(ball_positions)):
            current_bbox= ball_positions[i].get(1,{}).get('bbox',[])

            if len(current_bbox) == 0:
                continue

            if last_good_frame_index==-1:
                last_good_frame_index=i
                continue

            last_good_box = ball_positions[last_good_frame_index].get(1,{}).get('bbox',[])
            frame_gap = i - last_good_frame_index
            adjusted_max_distance= maximum_allowed_distance * frame_gap

            if np.linalg.norm(np.array(last_good_box[:2]) - np.array(current_bbox[:2]))> adjusted_max_distance:
                ball_positions[i]={}
            else:
                last_good_frame_index=i


        return ball_positions
    
    def interpolate_ball_positions(self,ball_positions):

        extracted_positions = []
        for x in ball_positions:
            bbox = x.get(1, {}).get('bbox', [])
            if len(bbox) == 4:
                extracted_positions.append(bbox)
            else:
                extracted_positions.append([None, None, None, None])  # Fill missing


        df_ball_positions = pd.DataFrame(ball_positions,columns=["x1","y1","x2","y2"])

        #interpolate missing values
        df_ball_positions = df_ball_positions.interpolate(limit_direction='both')
        df_ball_positions = df_ball_positions.bfill()
        df_ball_positions = df_ball_positions.ffill()  # Fill leading NaNs

        ball_positions =[{1:{"bbox":x}} for x in df_ball_positions.to_numpy().tolist() ]

        return ball_positions
