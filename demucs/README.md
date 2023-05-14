# Demucs

Before using the trained models to separate songs, install dependencies from `requeirements.txt`.

We include 5 trained models in the `release_models` directory. The models are:
- *0b6894ef* - Remix (12 channels, 3 depth), 
- *9af80a6a* - Medley (12 channels, 3 depth), 
- *af9a0947* - Remix + Medley (12 channels, 3 depth)
- *195c4583* - Remix + Medley (24 channels, 6 depth), 
- *442d1ed0* - Remix + Medley (28 channels, 6 depth).

To separate any desired track using these models, run:
```
python separateTracks.py SONG_PATH -d cpu/cuda -n MODEL_SIGNATURE --mp3 --repo ./release_models
```
Separated tracks will appear in the `separated` folder.