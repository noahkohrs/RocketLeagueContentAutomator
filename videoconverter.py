from moviepy.editor import VideoFileClip, CompositeVideoClip
from moviepy.video import fx

def resize_video(filename, arival = 'new_short.mp4') -> str:
    clip = VideoFileClip(filename)
    
    # Déterminez la hauteur et la largeur souhaitées

    desired_height = 1280
    desired_width = int(desired_height * 9 / 16)
    black_bar_height = 200

    # Redimensionnez d'abord la hauteur du clip à la hauteur souhaitée
    clip_resized = clip.resize(height=desired_height - black_bar_height*2)


    # Sinon, coupez les parties excédentaires de la vidéo
    cropped_clip = clip_resized.crop(x_center=clip_resized.w/2, width=desired_width)

    # Ajoutez des barres noires en haut et en bas pour obtenir un rapport hauteur / largeur de 16: 9
    padded_clip = cropped_clip.fx(fx.all.margin, top=black_bar_height, bottom=black_bar_height, left=0, right=0)

    final_clip = CompositeVideoClip([padded_clip])
    # Render on graphics card with a video codec that is not libx264
    final_clip.write_videofile(arival, codec='libx264', remove_temp=True, audio_codec='aac', threads=4, bitrate='5000k')

    
    return arival

if __name__ == '__main__':
    filename = 'test.mp4'
    resize_video(filename)