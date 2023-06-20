# Application for Guitar Sound Separation from Music Recording

Author: Natália Holková (xholko02)

This thesis aims to implement a model capable of separating guitar sounds from a recording and use it in a practical application. It was necessary to manually create our dataset from remixes of songs and modify the existing MedleyDB dataset for our purposes. We have chosen Demucs architecture as a basis for our neural network. We trained it from scratch to separate audio files into five distinct recordings containing drums, bass, vocals, guitars, and other accompaniment. We trained five models on MetaCentrum, which we evaluated objectively and subjectively. The implemented application serves as both a music player and an educational tool. The main feature is to allow users to listen to isolated instruments, for example, a guitar, and therefore more easily learn songs by ear. The application was subjected to user testing, and the knowledge learned will be used in future development.

The included medium contains:
- `documentation` - directory with thesis text source code and pdf
- `demucs` - directory with code and datasets used for training the neural networks
- `musicSeparationGUI` - directory with code and instructions on how to launch the practical application
- `examples` - directory with examples of separated songs
- `music_separation_training.xlsx` - an Excel file containing more information on the training process and results
