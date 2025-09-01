##part 1 of the codes

# import numpy as np
# from .utils import draw_triangle 

# class BallTracksDrawer:
#     def __init__(self):
#         self.ball_pointer_color = (0,255,0)

#     def draw(self,video_frames,tracks):
#         output_video_frames=[]
#         for frame_num, frame in enumerate(video_frames):
#             output_frame=frame.copy()

#             if frame_num < len(tracks):
#                 ball_dict = tracks[frame_num]
#                 for _, track in ball_dict.items():
#                     bbox = track.get('bbox', [])
#                     if not bbox or len(bbox) != 4 or any(np.isnan(bbox)):
#                         continue

#                     output_frame = draw_triangle(output_frame, bbox, self.ball_pointer_color)

#             output_video_frames.append(output_frame)

#         return output_video_frames


##part 2 of the codes
import numpy as np
from .utils import draw_triangle

class BallTracksDrawer:
    def __init__(self):
        self.ball_pointer_color = (0, 255, 0)  # Green triangle for ball

    def draw(self, video_frames, tracks):
        output_video_frames = []

        for frame_num, frame in enumerate(video_frames):
            frame = frame.copy()

            if frame_num < len(tracks):
                ball_dict = tracks[frame_num]

                for _, track in ball_dict.items():
                    bbox = track.get('bbox', [])

                    # Ensure bbox is valid and not containing NaNs
                    if (
                        not isinstance(bbox, (list, tuple, np.ndarray))
                        or len(bbox) != 4
                        or any(np.isnan(bbox))
                    ):
                        continue

                    # Draw green triangle on the ball
                    frame = draw_triangle(frame, bbox, self.ball_pointer_color)

            output_video_frames.append(frame)

        return output_video_frames
