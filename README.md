# Reddit Bot Detector

A Python-based machine learning project designed to detect bot accounts on Reddit. It analyzes user activity, content, and profile patterns to generate a "bot confidence score."

This project is built using `scikit-learn` for machine learning, `praw` for interacting with the Reddit API, and is fully containerized using **Docker**.

---

## Features

* **Machine Learning Model**: Uses a `RandomForestClassifier` trained on various user metrics.
* **Feature Analysis**: Evaluates features like comment similarity, activity timing, karma ratios, and name patterns.
* **Reddit API**: Uses PRAW to fetch live user data.
* **Dockerized**: Easily build and run the entire application in a container using `docker-compose`.

---

## Tech Stack

* **Backend**: Python
* **API**: PRAW (Reddit API Wrapper)
* **ML Stack**: scikit-learn, pandas, numpy
* **Containerization**: Docker & Docker Compose

---

## Getting Started

### Prerequisites

* [Docker](https://www.docker.com/products/docker-desktop/)
* [Python 3.10+](https://www.python.org/)
* A Reddit App (for API credentials). You can create one [here](https://www.reddit.com/prefs/apps).

### 1. Clone the Repository

```bash
git clone [https://github.com/YourUsername/RedditBotDetector.git](https://github.com/YourUsername/RedditBotDetector.git)
cd RedditBotDetector
```
2. Set Up Environment Variables
This project requires Reddit API credentials. Create a file named .env in the root of the project.

Never push this file to Git!

# .env
```bash
REDDIT_CLIENT_ID=Your_Client_ID_Here
REDDIT_CLIENT_SECRET=Your_Client_Secret_Here
REDDIT_USER_AGENT=A_Descriptive_User_Agent (e.g., BotDetector v1.0 by u/YourUsername)
REDDIT_USERNAME=Your_Reddit_Username
REDDIT_PASSWORD=Your_Reddit_Password
```

You can run this project using Docker (recommended) or locally with a Python virtual environment.

A. Docker (Recommended)
This is the simplest way to get up and running.

Build the image:

```bash
docker-compose build
```
Run the container:
```bash
docker-compose up
```

Run the main detector script:

```bash

python src/bot_detector.py
```
Training Data & Privacy

The training data for this project is private and not included in this repository.

This includes the following files, which are listed in the .gitignore:

known_bots.py

known_humans.py

training_data.csv

bot_detector_model.pkl

scaler.pkl

To train your own model, you will need to:

Create your own known_bots.py and known_humans.py lists.

Run scripts/build_dataset.py to fetch data and create your training_data.csv.

Run scripts/train_model.py to generate your own bot_detector_model.pkl.
