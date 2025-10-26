Generative Text Model – DTE-2501 AI Methods and Applications  

This project was developed as part of ¨Graded assignment 1 in the course DTE-2501 AI Methods and Applications 
The goal was to implement and explore simple generative text models in Natural Language Processing (NLP), starting with a Markov chain text generator and extending the work to include a Hidden Markov Model (HMM).  



Project Overview:  
Markov Model: 
  Implemented from scratch in Python. Trains on a dataset of text (in my case, anime subtitles) and generates new sentences based on word-to-word probabilities.  

User Interface (UI):
  A custom Matrix-inspired console UI (`ui_client.py`) lets the user generate sentences interactively, save them to file, and retrain on new datasets.  

Hidden Markov Model (HMM):  
  Adapted from an existing GitHub repository ([HMM-for-text-decryption](https://github.com/alessimichele/HMM-for-text-decryption)) to train on bigram states instead of for decryption. This was used to compare results with the Markov generator.  

For running preprocessing, markov model and UI please install dependencies trough requirements.txt:

conda create -n <enviroment> python=3.11 -y
conda activate <enviroment>

pip install -r requirements.txt

python src/ui_client.py
python src/preprocess.py
python src/markov_model.py
