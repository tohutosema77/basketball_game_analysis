from copy import deepcopy
import numpy as np
import cv2
import sys
from .homography import Homography
sys.path.append('../')
from utils import measure_distance,get_foot_position

class TacticalViewConverter:
    def __init__(self,court_image_path):
        self.court_image_path= court_image_path
        self.width=300
        self.height=161


        self.actual_width_in_meters=28
        self.actual_height_in_meters=15

        self.key_points = [
            # left edge
            (0,0),
            (0,int((0.91/self.actual_height_in_meters)*self.height)),
            (0,int((5.18/self.actual_height_in_meters)*self.height)),
            (0,int((10/self.actual_height_in_meters)*self.height)),
            (0,int((14.1/self.actual_height_in_meters)*self.height)),
            (0,int(self.height)),

            # Middle line
            (int(self.width/2),self.height),
            (int(self.width/2),0),
            
            # Left Free throw line
            (int((5.79/self.actual_width_in_meters)*self.width),int((5.18/self.actual_height_in_meters)*self.height)),
            (int((5.79/self.actual_width_in_meters)*self.width),int((10/self.actual_height_in_meters)*self.height)),

            # right edge
            (self.width,int(self.height)),
            (self.width,int((14.1/self.actual_height_in_meters)*self.height)),
            (self.width,int((10/self.actual_height_in_meters)*self.height)),
            (self.width,int((5.18/self.actual_height_in_meters)*self.height)),
            (self.width,int((0.91/self.actual_height_in_meters)*self.height)),
            (self.width,0),

            # Right Free throw line
            (int(((self.actual_width_in_meters-5.79)/self.actual_width_in_meters)*self.width),int((5.18/self.actual_height_in_meters)*self.height)),
            (int(((self.actual_width_in_meters-5.79)/self.actual_width_in_meters)*self.width),int((10/self.actual_height_in_meters)*self.height)),
        ]
    
    # def validate_keypoints(self,keypoints_list):


    #     keypoints_list = deepcopy(keypoints_list)
    #     for frame_idx,frame_keypoints in enumerate(keypoints_list):
    #         # frame_keypoints = frame_keypoints.xy.tolist()[0]

    #         # detected_indicies= [i for i, kp in enumerate(frame_keypoints) if kp[0]>0 and kp[1]>0]
    #         xy_list = frame_keypoints.xy.tolist()
        
    #         if not xy_list or len(xy_list[0]) == 0:
    #             continue  # skip this frame if no keypoints detected

    #         frame_keypoints_xy = xy_list[0]
    #         detected_indicies =[i for i, kp in enumerate(frame_keypoints_xy) if kp[0] > 0 and kp[1] > 0]

    #         if len(detected_indicies) < 3:
    #             continue

    #         invalid_keypoints=[]

    #         for i in detected_indicies:
    #             #skip keypoints (0,0)
    #             if frame_keypoints[i][0] ==0 and frame_keypoints[i][1] ==0:
    #                 continue

    #             other_indicies = [idx for idx in detected_indicies if idx!=i and idx not in invalid_keypoints]

    #             if len(other_indicies)<2:
    #                 continue

    #             j,k = other_indicies[0],other_indicies[1]
    #             #court view
    #             d_ij = measure_distance(frame_keypoints[i],frame_keypoints[j])
    #             d_ik = measure_distance(frame_keypoints[i],frame_keypoints[k])

    #             #done by tactical view
    #             t_ij = measure_distance(self.key_points[i],self.key_points[j])
    #             t_ik = measure_distance(self.key_points[i],self.key_points[k])

    #             if t_ij > 0 and t_ik > 0:
    #                 prop_detected = d_ij/d_ik if d_ik >0 else float('inf')
    #                 prop_tactical = t_ij/t_ik if t_ik >0 else float('inf')

    #                 error =(prop_detected-prop_tactical)/prop_tactical
    #                 error= abs(error)

    #                 if error> 0.8:
    #                     keypoints_list[frame_idx].xy[0][i] *=0
    #                     keypoints_list[frame_idx].xyn[0][i] *=0
    #                     invalid_keypoints.append(i)


    #     return keypoints_list
    def validate_keypoints(self, keypoints_list):
        keypoints_list = deepcopy(keypoints_list)
        
        for frame_idx, frame_keypoints in enumerate(keypoints_list):
            xy_list = frame_keypoints.xy.tolist()
            
            if not xy_list or len(xy_list[0]) == 0:
                continue  # skip this frame if no keypoints detected

            frame_keypoints_xy = xy_list[0]
            detected_indices = [i for i, kp in enumerate(frame_keypoints_xy) if kp[0] > 0 and kp[1] > 0]

            if len(detected_indices) < 3:
                continue

            invalid_keypoints = []

            for i in detected_indices:
                if frame_keypoints_xy[i][0] == 0 and frame_keypoints_xy[i][1] == 0:
                    continue

                other_indices = [idx for idx in detected_indices if idx != i and idx not in invalid_keypoints]
                if len(other_indices) < 2:
                    continue

                j, k = other_indices[0], other_indices[1]

                # court view
                d_ij = measure_distance(frame_keypoints_xy[i], frame_keypoints_xy[j])
                d_ik = measure_distance(frame_keypoints_xy[i], frame_keypoints_xy[k])

                # tactical view
                t_ij = measure_distance(self.key_points[i], self.key_points[j])
                t_ik = measure_distance(self.key_points[i], self.key_points[k])

                if t_ij > 0 and t_ik > 0:
                    prop_detected = d_ij / d_ik if d_ik > 0 else float('inf')
                    prop_tactical = t_ij / t_ik if t_ik > 0 else float('inf')

                    error = abs((prop_detected - prop_tactical) / prop_tactical)

                    if error > 0.8:
                        keypoints_list[frame_idx].xy[0][i] *= 0
                        keypoints_list[frame_idx].xyn[0][i] *= 0
                        invalid_keypoints.append(i)

        return keypoints_list

    
    def  transform_players_to_tactical_view(self,keypoints_list,player_tracks):
        tactical_player_positions = []

        for frame_idx,(frame_keypoints,frame_tracks) in enumerate(zip(keypoints_list,player_tracks)):

            tactical_positions= {}

            frame_keypoints = frame_keypoints.xy.tolist()[0]

            if frame_keypoints is None or len(frame_keypoints)==0:
                tactical_player_positions.append(tactical_positions)
                continue

            detected_keypoints = frame_keypoints

            valid_indicies =[i for i,kp in enumerate(detected_keypoints) if kp[0]>0 and kp[1]>0]

            if len(valid_indicies)<4:
                tactical_player_positions.append(tactical_positions)
                continue

            source_points = np.array([detected_keypoints[i] for i in valid_indicies],dtype=np.float32)
            target_points = np.array([self.key_points[i] for i in valid_indicies],dtype=np.float32)

            try:
                homography = Homography(source_points,target_points)

                for player_id,player_data in frame_tracks.items():
                    bbox = player_data["bbox"]
                    player_position = np.array([get_foot_position(bbox)])

                    transformed_point = homography.transform_points(player_position)
                    if len(transformed_point) > 0:
                        tactical_positions[player_id] = transformed_point[0].tolist()

            except (ValueError,cv2.error) as e:
                pass

            tactical_player_positions.append(tactical_positions)

        return tactical_player_positions