# Finance Quiz App

An interactive **Finance Quiz Dashboard** built with **Streamlit** and **OpenAI API**. This app assesses the user's knowledge in basic financial concepts, provides micro-learning modules, and dynamically adapts the quiz difficulty based on user performance.

---

## Features

- Collects user's name and begins a quiz journey
- Generates 7 initial questions using OpenAI API on a basic finance topic
- Analyzes responses to evaluate current skill level
- Provides a brief learning module based on the initial score
- Asks 3 follow-up questions on the newly introduced topic
- Unlocks and transitions to a new module based on user's score
- Dynamic and adaptive learning experience

---

## Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **Backend**: Python, OpenAI GPT API
- **Others**: Git, GitHub, `.env` for API key management

---

## Installation

1. **Clone the repository**
- git clone https://github.com/your-username/finance-quiz-app.git
- cd finance-quiz-app

2. **Create virtual environment & install dependencies**
- python -m venv venv
- source venv/bin/activate     # On Windows: venv\Scripts\activate
- pip install -r requirements.txt

3. **Set up OpenAI API Key**
- Create a .env file in the root or backend directory and add:
  - OPENAI_API_KEY=your-api-key-here

4. **Run the Streamlit app**
- streamlit run app.py

---

## Contributing
- Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## Acknowledgements
- Streamlit
- OpenAI

---

## Future Improvements
- Add leaderboard functionality
- Save user progress and history
- Include more diverse financial modules
- Enhance UI with better visualization

