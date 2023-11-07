from moviepy.editor import VideoFileClip, CompositeVideoClip
from moviepy.video import fx

def resize_video(filename, arival = 'new_short.mp4') -> str:
    clip = VideoFileClip(filename)

    desired_height = 1280
    desired_width = int(desired_height * 9 / 16)
    black_bar_height = 200
    boost_size = 180

    # Resize to the wanted height.
    clip_resized = clip.resize(height=desired_height - black_bar_height*2)


    # Cutout overflowing parts of the video.
    cropped_clip = clip_resized.crop(x_center=clip_resized.w/2, width=desired_width)

    # Adding black bars.
    padded_clip = cropped_clip.fx(fx.all.margin, top=black_bar_height, bottom=black_bar_height, left=0, right=0)

    # Showing the boost left.
    boost = clip.fx(fx.all.crop, x1=clip.w-295, y1=clip.h-295 ,x2=clip.w-40, y2=clip.h-40)
    boost = boost.resize(height=boost_size)
    boost = boost.set_position(((desired_width-boost_size)/desired_width, (desired_height-boost_size-black_bar_height)/desired_height), relative=True)
    boost = boost.margin(right=0, top=0)

    boost = boost.set_duration(clip.duration-4)
    boost = boost.set_opacity(0.85)
    
    final_clip = CompositeVideoClip([padded_clip, boost])

    final_clip.write_videofile(arival, codec='libx264', remove_temp=True, audio_codec='aac', threads=4, bitrate='5000k')

    
    return arival

if __name__ == '__main__':
    filename = 'test.mp4'
    resize_video(filename)
