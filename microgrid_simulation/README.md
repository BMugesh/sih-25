# Microgrid Controller Credit Transfer Simulation

A Python-based simulation of a controller-mediated microgrid credit transfer system. This project demonstrates how houses in a microgrid can exchange energy credits through a central controller while maintaining transaction integrity and balance validation.

## Features

- Peer-to-peer energy credit transfers between houses
- Central microgrid energy supply
- Controller-mediated transfer validation
- Real-time balance tracking
- Transaction logging
- Interactive Streamlit UI
- MongoDB for persistent storage

## Prerequisites

1. Python 3.8 or higher
2. MongoDB Compass (local installation) or MongoDB Atlas account
3. pip (Python package installer)

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd microgrid_simulation
   ```

2. Create a virtual environment (recommended):

   ```bash
   python -m venv venv

   # Activate on Windows
   .\venv\Scripts\activate

   # Activate on macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start MongoDB:
   - If using MongoDB Compass locally, ensure it's running on `mongodb://localhost:27017`
   - If using MongoDB Atlas, create a `.env` file with your connection string

## Running the Application

1. Ensure MongoDB is running

2. Start the Streamlit application:

   ```bash
   streamlit run src/app.py
   ```

3. Open your browser and navigate to the displayed URL (typically http://localhost:8501)

## Project Structure

- `src/`
  - `app.py` - Main Streamlit application
  - `controller.py` - MicrogridController class implementation
  - `database.py` - MongoDB connection and operations
  - `simulation.py` - Simulation logic for random transfers
  - `models/` - Data models and utility functions

## Usage

1. **User Dashboard**: View all users and their current energy/credit balances
2. **Transfer Credits**: Make energy credit transfers between houses or with the microgrid
3. **Transaction Log**: View history of all transfers
4. **Simulation**: Run automated random transfers to simulate microgrid activity

## Error Handling

- Insufficient balance checks
- Invalid user ID validation
- Database connection error handling
- Transaction integrity validation

## Contributing

Feel free to submit issues and enhancement requests.
