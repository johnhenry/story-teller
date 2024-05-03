# Story Teller

Story teller allows you to piece together a story using AI.

Visit pages directly `/{page_number}` or visit `/` to get a random page.

Pages that do not exist will be automagically generated.

## Requirements

- [conda](https://conda.io)

## Setup

### Create environment

```shell
conda env create -f environment.yml
```

### Activate environment

```shell
conda activate story-teller
```

### Install dependencies

```shell
pip install -r requirements.txt
```

### Set environment variables

```shell
export GROQ_API_KEY=<get from https://console.groq.com/keys>
```

### Run

```shell
python main.py
```

### Vist

Vist [http://localhost:8080](http://localhost:8080)
