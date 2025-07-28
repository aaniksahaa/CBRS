# 🩸 CBRS - Cognitive Blood Request System

<!-- [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/Node.js-16+-green.svg)](https://nodejs.org/)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org/) -->

A comprehensive system for detecting, parsing, and responding to blood donation requests in social media messages. CBRS uses advanced machine learning models to identify blood request messages and extract structured information to facilitate quick donor matching and notification.

---

## 🎯 Overview

The Cognitive Blood Request System (CBRS) is designed to automatically process blood donation requests from various social media platforms. The system employs:

- **Binary Classification**: Identifies whether a message is a blood request
- **Information Extraction**: Parses relevant details like blood type, location, urgency, contact information
- **Donor Management**: Maintains a database of registered donors
- **Multi-platform Support**: Telegram and Discord bot integration
- **Web Interface**: User-friendly donor registration and management

## ✨ Features

- 🔍 **Intelligent Message Detection**: Binary classification of blood request messages
- 📝 **Information Parsing**: Extract structured data (blood type, location, contact, etc.)
- 🌐 **Multi-language Support**: Bengali, English, and Transliterated Bengali
- 🤖 **Bot Integration**: Telegram and Discord bots for real-time processing
- 💻 **Web Dashboard**: React-based frontend for donor registration
- 🏗️ **Robust Backend**: Node.js API with MongoDB database
- 📊 **Comprehensive Analytics**: Detailed results and performance metrics

---

## 📁 Project Structure

```
CBRS/
├── 📁 dataset/                          # Training and evaluation datasets
│   ├── parsed_merged.json              # Structured message-JSON pairs
│   ├── sharegpt_dataset.jsonl          # ShareGPT format dataset
│   ├── train.jsonl / validation.jsonl / test.jsonl
│   └── pre_parsed/                      # Pre-processed classification data
├── 📁 binary-classifier/               # Binary classification models
│   └── eval/                           # Evaluation notebooks
├── 📁 parser-llama-finetuning/         # LLama-3.2-3B fine-tuning notebooks
├── 📁 results/                         # Model evaluation results and plots
│   ├── classifier-results/             # Classification performance metrics
│   ├── parser-results/                 # Parsing accuracy results
│   └── dataset_stats/                  # Dataset statistics
├── 📁 backend/                         # Node.js backend API
│   ├── controllers/                    # API controllers
│   ├── routes/                         # API routes
│   ├── prisma/                         # Database schema and migrations
│   └── middlewares/                    # Custom middleware
├── 📁 frontend/                        # React frontend application
│   ├── src/                           # Source code
│   └── public/                        # Static assets
├── 📁 telegram-bot/                    # Telegram bot implementation
├── 📁 discord-bot/                     # Discord bot implementation
├── 📁 utils/                          # Shared utility functions
└── 📁 assets/                         # Project assets and documentation
```

---

## 🚀 Quick Start

### Prerequisites

- **Python** 3.8 or higher
- **Node.js** 16 or higher
- **MongoDB** (for backend)
- **Git** for version control

### 🔧 Installation

1. **Clone the repository**

2. **Set up the backend**
   ```bash
   cd backend
   npm install
   ```

3. **Set up the frontend**
   ```bash
   cd frontend
   npm install
   ```

4. **Set up the Telegram bot**
   ```bash
   cd telegram-bot
   pip install -r requirements.txt
   ```

---

## 🎮 Usage

### 💻 Web Application

1. **Start the backend server**
   ```bash
   cd backend
   npm start
   ```
   The API will be available at `http://localhost:3000`

2. **Launch the frontend**
   ```bash
   cd frontend
   npm run dev
   ```
   The web interface will be available at `http://localhost:5173`

### 🤖 Telegram Bot

1. **Configure environment variables**
   ```bash
   cd telegram-bot
   # Create .env file with your Telegram bot token and OpenAI API key
   ```

2. **Start the bot**
   ```bash
   python main.py
   ```

### 🎮 Discord Bot

1. **Navigate to Discord bot directory**
   ```bash
   cd discord-bot
   npm install
   ```

2. **Configure and start**
   ```bash
   # Add your Discord bot token to configuration
   npm start
   ```

---

## 📊 Datasets

### 🔍 Classification Dataset
- **Location**: `dataset/pre_parsed_merged.json`
- **Content**: Messages labeled as blood requests or non-requests
- **Languages**: Bengali, English, Transliterated Bengali
- **Public Access**: [Kaggle Dataset](https://www.kaggle.com/datasets/aaniksahaa/bnet-dataset)

### 📝 Parsing Dataset
- **Location**: `dataset/parsed_merged.json`
- **Content**: Message-JSON pairs for information extraction
- **Format**: ShareGPT style with 80:10:10 train-validation-test split
- **Public Access**: [HuggingFace Dataset](https://huggingface.co/datasets/imAniksahA/CBRS-parsing)

---

## 🧠 Models

### 🎯 Binary Classifier
- **Purpose**: Identify blood request messages
- **Training**: Located in `binary-classifier/` directory
- **Evaluation**: Comprehensive evaluation notebooks in `binary-classifier/eval/`

### 🔍 Parser
- **Base Model**: LLama-3.2-3B
- **Fine-tuning**: LoRA using Unsloth framework
- **Training**: Notebooks available in `parser-llama-finetuning/`
- **Platform**: Trained on Kaggle infrastructure

---

## 📈 Results

Detailed evaluation results for the classifier and parser and performance visualizations are available in the `results/` directory:

- **Classification Metrics**: Precision, Recall, F1-scores
- **Parsing Accuracy**: Entity extraction performance
- **Performance Plots**: Visual analysis of model performance
- **Dataset Statistics**: Comprehensive data analysis

---

## 🛠️ API Reference

### Backend Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/donors/register` | Register a new donor |
| `GET` | `/api/donors` | Retrieve donor list |
| `POST` | `/api/notifications` | Send emergency notifications |
| `GET` | `/api/statistics` | Get system statistics |

### Bot Commands

#### Telegram Bot
- `/start` - Initialize bot interaction
- `/help` - Show available commands
- `/parse` - Parse a blood request message

---
