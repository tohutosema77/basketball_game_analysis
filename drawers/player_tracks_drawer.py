##part 1
from .utils import draw_ellipse,draw_triangle
class PlayerTrackersDrawer:
    
    def __init__(self,team_1_color=[255,245,238],team_2_color=[128,0,0]):

        self.default_player_team_id=1

        self.team_1_color = team_1_color
        self.team_2_color = team_2_color

    # def draw(self, video_frames, tracks):

    #     output_video_frames= [] #an empty list for now
    #     for frame_num, frame in enumerate(video_frames):
    #         frame = frame.copy()

    #         # if frame_num <len(tracks):
    #         #     break  # or continue if you still want to process remaining frames
    #         player_dict= tracks[frame_num]

    #         #Draw Players tracks
    #         for track_id, player in player_dict.items():
           
    #             frame = draw_ellipse(frame, player['box'],(0,0,255),track_id)

    #         output_video_frames.append(frame)

    #     return output_video_frames
    

   #part2
    def draw(self, video_frames, tracks, player_assignment, ball_aquisition):
        output_video_frames = []
        for frame_num, frame in enumerate(video_frames):
            frame = frame.copy()

            if frame_num < len(tracks):
                player_dict = tracks[frame_num]
                assignment_for_frame = player_assignment[frame_num]
                player_with_ball = ball_aquisition[frame_num]

                for track_id, player in player_dict.items():
                    bbox = player['bbox']
                    team_id = assignment_for_frame.get(track_id, self.default_player_team_id)

                    color = self.team_1_color if team_id == 1 else self.team_2_color

                    # Draw ellipse with ID
                    frame = draw_ellipse(frame, bbox, color, track_id)

                    # If this player has the ball, draw a red triangle
                    if track_id == player_with_ball:
                        frame = draw_triangle(frame, bbox, (0, 0, 255))  # Red

            output_video_frames.append(frame)

        return output_video_frames