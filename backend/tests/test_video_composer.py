from ml_models.video_composer import VideoComposer


print("Starting Video Composer Test...")


composer = VideoComposer()


storyboard = [

    {
        "scene_number": 1,
        "scene": "Organic farm",
        "media_type": "video",
        "media_path": "datasets/clips/video1_clip001.mp4",
        "duration": 5
    },

    {
        "scene_number": 2,
        "scene": "Fresh vegetables",
        "media_type": "video",
        "media_path": "datasets/clips/video2_clip001.mp4",
        "duration": 5
    },

    {
        "scene_number": 3,
        "scene": "Modern tractors",
        "media_type": "video",
        "media_path": "datasets/clips/video4_clip001.mp4",
        "duration": 5
    }
]


output = composer.compose(
    storyboard=storyboard,
    music_path=None,
    output_name="test_composed_video.mp4"
)


print("\nFinal Output:")
print(output)