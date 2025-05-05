# Model Training

This folder contains scripts for preprocessing and training machine learning models.

## Contents

* **Preprocessing**: Scripts for preparing the data:

  * `preprocces_create_pre_training_files.py`: Creates a more manageable CSV file from the database for training on a compute cluster.
  * `preprocces_map_pre_trained_files_with_temperature_and_frequency.py`: Maps individual data points to the corresponding temperature and frequency files. For performance reasons, these files were not fully stored in the database.
  * `preprocces_match_keyence_to_production.py`: Keyence measurements must be mapped to production timestamps to ensure correct alignment with the corresponding production data.

* **Training**: Scripts for training and evaluating ML models. Various parameter experiments are included:

  * `train_cluster_model.py`: Trains a model to predict Keyence measurement values.
  * `train_taster_model.py`: Trains a model to predict Taster values.

## Requirements

* Python 3.8 or higher
* Install the required dependencies using:

  ```bash
  pip install -r requirements.txt
  ```

## Contributing

Contributions are welcome! Please open a pull request or submit an issue for feedback or suggestions.

