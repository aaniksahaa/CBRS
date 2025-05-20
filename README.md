This codebase accompanies CBRS(Cognitive Blood Request System).

# Datasets

## Pre-parsed Dataset

This dataset contains simply the text messages and their origin. This dataset can be found at `dataset/pre_parsed_marged.json`. It contains samples across Bengali, English, Transliterated Bengali and both positive and negative samples. We mainly use this dataset to train the classifier model.

## Parsed Dataset

This dataset contains pairs of text messages and their corresponding structured JSON. This dataset can be found at `dataset/parsed_marged.json`. We further create a sharegpt style dataset and upload it to huggingface with 80:10:10 train-valdation-test split.

# Models

## Classifier

The code for training and evaluationg the classifiers can be found at `binary_classifier` directory.

## Parser

The code for finetuning LLama-3.2-3B with our parsing dataset using LoRA can be found at `finetuning` directory.




