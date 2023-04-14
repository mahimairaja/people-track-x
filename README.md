<p align="center">
  <a href="" rel="noopener">
 <img width=600px height=250px src="asset/header.png" alt="Project logo"></a>
</p>
<h3 align="center">People <span style="color : #9eeade">Track-X</span></h3>

<div align="center">

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)

</div>

---

<p align="center" style="padding-left : 50px;padding-right : 50px;">
“An effienct way of crowd density analysis”
</p>


<details>
<summary> Website UI Look
</summary>
<img src='asset/webpage.jpg'>
</details>


<figure align="center" >
  <img src="asset/graph.png" alt="Graph" width=600px height=350px>
  <figcaption>Line Plot - Time vs Count.</figcaption>
</figure>

## Quick Start 🚀 :

### Method 01 - Using `virtual environment` 📦

1) Clone the Repository [People-Track-X](https://github.com/mahimairaja/People-Track-X)

```bash
git clone https://github.com/mahimairaja/People-Track-X.git

cd People-Track-X
```

2) Create a virtual environment

```bash
python -m venv env
```
   
3) Activate the virtual environment (Run according to your system)
```bash
source env/bin/activate 
# This is for linux or mac OS

.\env\Script\activate  
# This is for windows OS
```

3) Install the dependencies
```bash
pip install -r requirements.txt
```

4) Run the streamlit app
```bash
cd app

streamlit run app.py
```

### Method 02 - Using `Docker container 🚢` 

1) Clone the Repository [People-Track-X](https://github.com/mahimairaja/People-Track-X)

```bash
git clone https://github.com/mahimairaja/People-Track-X.git

cd People-Track-X
```

2) Build the container

```bash
docker build -t people-track-x .
```

2) Execute the container

```bash
docker run -p 8501:8501 people-track-x
```
----

### Algorithm 📝 : 
1. Object Detection - YoloV8
1. Object Tracking - Byte Tracker

---
Thank you visiting !

Reach me 📩 - [Mahimai Raja J](https://www.linkedin.com/in/mahimairaja/) 

## Licence <a name = "license"></a>

The contents of this project are Copyright (c) [Mahimai Raja J](https://www.linkedin.com/in/mahimairaja/). 

All rights reserved.


    While using kindly provide attribution by citing this repository.


