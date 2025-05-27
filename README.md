<a name="readme-top"></a>

<br />
<div align="center">
  <h1 align="center">Ai-driven-turning-machine-optimizer</h1>

  <p align="center">
    <a href="https://github.com/Green-AI-Hub-Mittelstand/readme_template/issues">Report Bug</a>
    ·
    <a href="https://github.com/Green-AI-Hub-Mittelstand/readme_template/issues">Request Feature</a>
  </p>

  <br />

  <p align="center">
    <a href="https://www.green-ai-hub.de">
    <img src="images/green-ai-hub-keyvisual.svg" alt="Logo" width="80%">
  </a>
    <br />
    <h3 align="center"><strong>Green-AI Hub Mittelstand</strong></h3>
    <a href="https://www.green-ai-hub.de"><u>Homepage</u></a> 
    | 
    <a href="https://www.green-ai-hub.de/kontakt"><u>Contact</u></a>
  </p>
</div>

<br/>

## About The Project

This project was developed as part of the Green-AI Hub pilot initiative in collaboration with the company Heismann. The aim was to optimize internal processes through AI-driven solutions.

Two main use cases were addressed:

1. **Machine Warm-up Time Analysis**: Statistical analysis was performed to determine the optimal start temperature of machines based on part production data and temperature measurements.

2. **Part Dimension Prediction**: Machine learning models were trained to predict the deviation of part dimensions from optimal values, allowing early detection of defective parts with significant deviations.

To protect company-sensitive data, some scripts and the database were excluded from publication. Additional anonymization steps were performed, so some scripts may be incomplete or placeholder-based.

### Folder Structure

Since no final prototype was developed, the project has been organized into logical folders representing individual work steps:

1. **Database**: PostgreSQL-based database. Scripts for loading and reading data are provided. To use it, start a PostgreSQL instance and either restore a backup using the provided batch file or configure a fresh one via `config.json`.

   **Note**: The actual database is not publicly included. It contains all project-related data, including:
  - Measurement data of the components
  - Temperature data
  - Vibration data
  - Machine energy data
  - Axis settings
  - Tool changes
  - Production times
  - Rotational speeds
  - ...

2. **Dataparser**: All raw data (TXT and CSV) was collected from machines and provided by the company. These files were parsed and imported into the database using specialized scripts—each file type required its own parser due to inconsistent formats.

3. **Model\_Training**: Models were trained on a computing cluster using TPOT AutoML. Various preprocessing steps were applied to prepare optimal training data. Due to their high frequency, temperature and frequency data were not loaded into the database but joined directly from the original files during training.

4. **Visualisations**: Contains all scripts used to generate visual representations of the data. Each file describes the purpose of the specific visualization.

5. **Experimental**: Contains an unfinished third use case: a statistical analysis of tool lifespan. Some initial scripts for formula definition and visual evaluation are included. This area was not further developed.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Table of Contents

<details>
  <summary><img src="images/table_of_contents.jpg" alt="Logo" width="2%"></summary>
  <ol>
    <li><a href="#about-the-project">About The Project</a></li>
    <li><a href="#table-of-contents">Table of Contents</a></li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Getting Started

Clone this repository, open a terminal, and navigate to the project directory.

### Installation

To install the required Python dependencies, run:

```bash
pip install -r requirements.txt
```

To set up your own PostgreSQL instance, install PostgreSQL via [this link](https://www.postgresql.org/download/) and configure your database as described in the **Database** folder.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Usage

⚠️ **Note**: Currently, the scripts are tested only with Python 3.8.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contributing

Contributions are what make the open-source community such a great place to learn, inspire, and grow. Any contributions you make are **greatly appreciated**.

If you have a suggestion for improvement, please fork the repository and submit a pull request. You can also open an issue with the tag `"enhancement"`.

Don't forget to ⭐ the project. Thank you!

**Steps to contribute:**

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## License

Distributed under the MIT License. See `LICENSE.txt` for details.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contact

**Green-AI Hub Mittelstand** – [info@green-ai-hub.de](mailto:info@green-ai-hub.de)
Project Link: [https://github.com/Green-AI-Hub-Mittelstand/repository\_name](https://github.com/Green-AI-Hub-Mittelstand/repository_name)

<br />
<a href="https://www.green-ai-hub.de/kontakt"><strong>Get in touch »</strong></a>
<br /><br />

<p align="left">
  <a href="https://www.green-ai-hub.de">
    <img src="images/green-ai-hub-mittelstand.svg" alt="Logo" width="45%">
  </a>
</p>

<p align="right">(<a href="#readme-top">back to top</a>)</p>
