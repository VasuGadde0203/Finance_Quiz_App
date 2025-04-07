# import streamlit as st
# import requests
# import os
# from dotenv import load_dotenv

# load_dotenv()

# API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/quiz")  # Replace with your backend URL

# st.set_page_config(page_title="Finance Quiz Game", layout="centered")

# # Session state variables
# if "user_id" not in st.session_state:
#     st.session_state["user_id"] = None
# if "score" not in st.session_state:
#     st.session_state["score"] = 0
# if "level" not in st.session_state:
#     st.session_state["level"] = "Beginner"
# if "question" not in st.session_state:
#     st.session_state["question"] = None

# # Home Page: Ask for username
# st.title("📊 Finance Quiz Game")
# st.write("Test your finance knowledge and level up!")

# if st.session_state["user_id"] is None:
#     user_name = st.text_input("Enter your name to start:")
#     if st.button("Start Quiz"):
        
#         response = requests.post(f"{API_BASE_URL}/start_quiz", params={"user_name": user_name})
#         if response.status_code == 200:
#             data = response.json()
#             st.session_state["user_id"] = data["user_id"]
#             st.session_state["score"] = data["score"]
#             st.session_state["level"] = data["level"]
#             level = st.session_state["level"]
#             st.success(f"Welcome, {user_name}! Your current level: {level}")
#         else:
#             st.error("Error starting quiz. Please try again.")

# # Fetch new question
# if st.session_state["user_id"]:
    
#     if st.session_state["question"] is None:
#         user_id = st.session_state["user_id"]
#         response = requests.get(f"{API_BASE_URL}/get_question/{user_id}")
        
#         if response.status_code == 200:
#             result = response.json()  # Convert response to dictionary
#             st.session_state['question'] = result["question"]

#     if st.session_state["question"]:
#         question = st.session_state['question']
#         st.subheader(f"📝 Question ({st.session_state['level']} Level)")
#         st.write(question["question_text"])

#         selected_option = st.radio("Choose your answer:", question["options"], index=None)

#         if st.button("Submit Answer"):
#             if selected_option is None:
#                 st.warning("Please select an answer!")
#             else:
#                 selected_option_index = question["options"].index(selected_option)
#                 payload = {
#                     "user_id": st.session_state['user_id'],
#                     "question_id": question["_id"],
#                     "selected_option": selected_option_index,
#                     "correct_option": question["correct_option"], 
#                     "module": question["module"], 
#                     "explanation": question["explanation"]
#                 }
#                 response = requests.post(f"{API_BASE_URL}/submit_answer", params=payload)
#                 st.write("Got submitted response")
#                 if response.status_code == 200:
#                     result = response.json()
#                     st.session_state['score'] = result["new_score"]
#                     st.session_state['level'] = result["new_level"]

#                     if result["correct"]:
#                         st.success("✅ Correct!")
#                     else:
#                         st.error("❌ Incorrect!")

#                     st.write(f"📖 Explanation: {result['explanation']}")
#                     st.write(f"🏆 Your Score: {st.session_state['score']}")

#                     # Fetch next question
#                     st.session_state['question'] = None
#                 else:
#                     st.error("Error submitting answer. Please try again.")



import streamlit as st
import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/quiz")  # Replace with your backend URL

st.set_page_config(page_title="Finance Quiz Game", layout="centered")

# Session state variables
if "user_id" not in st.session_state:
    st.session_state["user_id"] = None
if "score" not in st.session_state:
    st.session_state["score"] = 0
if "level" not in st.session_state:
    st.session_state["level"] = "Beginner"
if "current_question" not in st.session_state:
    st.session_state["current_question"] = None
if "current_revision_question" not in st.session_state:
    st.session_state["current_revision_question"] = None
if "learning_mode" not in st.session_state:
    st.session_state["learning_mode"] = False
if "weak_topics" not in st.session_state:
    st.session_state["weak_topics"] = []
if "guide_text" not in st.session_state:
    st.session_state["guide_text"] = None
if "revision_questions" not in st.session_state:
    st.session_state["revision_questions"] = []

# Home Page: Ask for username
st.title("📊 Finance Quiz Game")
st.write("Test your finance knowledge and level up!")

# Step 1: User Registration
if st.session_state["user_id"] is None:
    user_name = st.text_input("Enter your name to start:")
    if st.button("Start Quiz"):
        response = requests.post(f"{API_BASE_URL}/start_quiz", params={"user_name": user_name})
        if response.status_code == 200:
            data = response.json()
            st.session_state["user_id"] = data["user_id"]
            st.session_state["score"] = data["score"]
            st.session_state["level"] = data["level"]
            st.session_state["topics"] = data["topics"]
            st.success(f"Welcome, {user_name}! Your current level: {st.session_state['level']}")
            st.session_state["current_question"] = None  # Fetch first question dynamically
        else:
            st.error("Error starting quiz. Please try again.")

# Step 2: Fetch & Display Next Question Dynamically
if st.session_state["user_id"] and not st.session_state["learning_mode"] and not st.session_state["revision_questions"]:
    
    # If no question is loaded, fetch one dynamically
    if st.session_state["current_question"] is None:
        user_id = st.session_state["user_id"]
        response = requests.get(f"{API_BASE_URL}/get_next_question/{user_id}", params={"user_id": st.session_state["user_id"]})
        if response.status_code == 200:
            question_response = response.json()
            st.session_state["current_question"] = question_response["question"]
        else:
            st.error("Error fetching next question. Try again.")

    # Display question
    if st.session_state["current_question"]:
        question = st.session_state["current_question"]
        st.subheader(f"📝 Question ({st.session_state['level']} Level)")
        st.write(question["question_text"])

        selected_option = st.radio("Choose your answer:", question["options"], index=None)

        if st.button("Submit Answer"):
            if selected_option is None:
                st.warning("Please select an answer!")
            else:
                print(f"Selected option: {selected_option}")
                selected_option_index = question["options"].index(selected_option)
                correct_option_index = question["correct_option_index"]
                correct_option = question["options"][correct_option_index]

                # Initialize or update topics dictionary
                topic_name = question["module"]
                if topic_name not in st.session_state["topics"]:
                    st.session_state["topics"][topic_name] = {"correct_answers": 0, "incorrect_answers": 0}
                
                print("question: ", question)
                if selected_option == correct_option:
                    st.success("✅ Correct!")
                    st.session_state["topics"][topic_name]["correct_answers"] += 1
                else:
                    st.error("❌ Incorrect!")
                    st.write(f"Correct Option: {correct_option}")
                    st.session_state["topics"][topic_name]["incorrect_answers"] += 1

                # Prepare the API payload
                payload = {
                    "user_id": st.session_state['user_id'],
                    "question_id": question["_id"],
                    "selected_option": selected_option, 
                    "correct_option": correct_option, 
                    "module": question['module'], 
                    "explanation": question["explanation"],
                    "topics": st.session_state["topics"],  # Now passing topics in API request
                    "question_type": "normal"
                }
                print(st.session_state["topics"])

                # Send the request to the API
                response = requests.post(f"{API_BASE_URL}/submit_answer", json=payload)

                # Process the response
                if response.status_code == 200:
                    result = response.json()
                    # print(result)
                    st.session_state['score'] = result["new_score"]
                    st.session_state['level'] = result["new_level"]

                    
                    # st.write(f"📖 Explanation: {result['explanation']}")
                    st.write(f"🏆 Your Score: {st.session_state['score']}")

                    # Clear current question to fetch a new one dynamically
                    st.session_state["current_question"] = None
                    
                    if result["learning_mode"]:
                        st.session_state["learning_mode"] = True
                
                    # Ask next question dynamically
                    if not result["learning_mode"]:
                        st.button("Next Question")
                else:
                    st.error("Error submitting answer. Please try again.")

        # If the backend determines the user has answered enough questions → switch to learning mode
        # if response.status_code == 200 and response.json().get("learning_mode", False):
        #     st.session_state["learning_mode"] = True

# Step 3: Learning Phase (AI Guide)
if st.session_state["learning_mode"] and not st.session_state["revision_questions"]:
    st.subheader("📚 Learning Mode: Strengthen Your Weak Areas")

    # Ensure only "Start Learning" button appears after 7 questions
    if not st.session_state["guide_text"]:
        if st.button("Start learning"):
            user_id = st.session_state["user_id"]
            response = requests.get(f"{API_BASE_URL}/get_learning_material", params={"user_id": user_id})

            if response.status_code == 200:
                st.session_state["guide_text"] = response.json()["learning_material"]
                st.write(st.session_state["guide_text"])
            else:
                st.session_state["guide_text"] = "Error fetching learning material. Try again."

    # Once learning is done, show "Start Revision Questions"
    if st.session_state["guide_text"]:
        if st.button("Start Revision Questions"):
            response = requests.get(f"{API_BASE_URL}/get_revision_questions", params={
                "user_id": st.session_state["user_id"],
                "learning_material": st.session_state["guide_text"]
            })
            if response.status_code == 200:
                st.session_state["revision_questions"] = response.json()["questions"]
                st.session_state["learning_mode"] = False
            else:
                st.error("Error fetching revision questions. Try again.")
                
# # Step 4: Revision Phase
# if st.session_state["revision_questions"] and not st.session_state["learning_mode"]:
    
#     if st.session_state["current_revision_question"] is None and st.session_state["revision_questions"]:
#         st.session_state["current_revision_question"] = st.session_state["revision_questions"].pop(0)

#     if st.session_state["current_revision_question"]:
#         question = st.session_state["current_revision_question"]
#         st.subheader("🔄 Revision Question")
#         st.write(question["question_text"])

#         selected_option = st.radio("Choose your answer:", question["options"], index=None, key=f"revision_{question['_id']}")

#         if st.button("Submit Revision Answer"):
#             if selected_option is None:
#                 st.warning("Please select an answer!")
#             else:
#                 selected_option_index = question["options"].index(selected_option)
                
#                 correct_option_index = question['correct_option_index']
#                 correct_option = question['options'][correct_option_index]
#                 payload = {
#                     "user_id": st.session_state['user_id'],
#                     "question_id": question["_id"],
#                     "selected_option": question['options'][selected_option_index], 
#                     "correct_option": correct_option,
#                     "module": question['module'], 
#                     "explanation": question["explanation"],
#                     "topics": st.session_state["topics"],
#                     "question_type": "revision"
#                 }
#                 response = requests.post(f"{API_BASE_URL}/submit_answer", json=payload)

#                 if response.status_code == 200:
#                     result = response.json()
#                     if result["correct"]:
#                         st.success("✅ Correct!")
#                     else:
#                         st.error("❌ Incorrect!")
#                         st.write(f"Correct Option: {correct_option}")

#                     st.session_state["current_revision_question"] = None

#                     if st.session_state["revision_questions"]:
#                         st.button("Next Revision Question")
#                 else:
#                     # No more questions left, reset session and show "Start Next Level Quiz"
#                     st.session_state["learning_mode"] = False
#                     st.session_state["revision_questions"] = None
#                     st.session_state["current_revision_question"] = None
#                     st.session_state["guide_text"] = None
#                     st.session_state["weak_topics"] = []
#                     st.button("Start Next Level Quiz") 
            
#         else:
#             st.error("Error submitting answer. Please try again.")


# Step 4: Revision Phase
if st.session_state["revision_questions"] and not st.session_state["learning_mode"]:
    
    # Initialize the current revision question if none exists
    try:
        if st.session_state["current_revision_question"] is None and st.session_state["revision_questions"]:
            st.session_state["current_revision_question"] = st.session_state["revision_questions"].pop(0)
    except IndexError:
        st.error("Error: No revision questions available.")
        st.session_state["current_revision_question"] = None
        st.session_state["revision_questions"] = None
        st.button("Start Next Level Quiz")
        

    # Display and process the current revision question
    if st.session_state["current_revision_question"]:
        question = st.session_state["current_revision_question"]
        st.subheader("🔄 Revision Question")
        st.write(question["question_text"])

        try:
            selected_option = st.radio("Choose your answer:", question["options"], index=None, key=f"revision_{question['_id']}")
        except KeyError:
            st.error("Error: Question options are missing or invalid.")
            

        if st.button("Submit Revision Answer"):
            if selected_option is None:
                st.warning("Please select an answer!")
            else:
                try:
                    selected_option_index = question["options"].index(selected_option)
                    correct_option_index = question['correct_option_index']
                    correct_option = question['options'][correct_option_index]

                    payload = {
                        "user_id": st.session_state['user_id'],
                        "question_id": question["_id"],
                        "selected_option": question['options'][selected_option_index], 
                        "correct_option": correct_option,
                        "module": question['module'], 
                        "explanation": question["explanation"],
                        "topics": st.session_state["topics"],
                        "question_type": "revision"
                    }

                    # Submit the answer to the API
                    response = requests.post(f"{API_BASE_URL}/submit_answer", json=payload)
                    response.raise_for_status()  # Raises an HTTPError for bad responses (4xx, 5xx)

                    if response.status_code == 200:
                        result = response.json()
                        if result["correct"]:
                            st.success("✅ Correct!")
                        else:
                            st.error("❌ Incorrect!")
                            st.write(f"Correct Option: {correct_option}")

                        st.session_state["current_revision_question"] = None

                        if st.session_state["revision_questions"]:
                            st.button("Next Revision Question")
                        else:
                            # No more questions left, reset session and show "Start Next Level Quiz"
                            st.session_state["learning_mode"] = False
                            st.session_state["revision_questions"] = None
                            st.session_state["current_revision_question"] = None
                            st.session_state["guide_text"] = None
                            st.session_state["weak_topics"] = []
                            st.button("Start Next Level Quiz")

                except requests.exceptions.RequestException as e:
                    st.error(f"Error submitting answer: {str(e)}. Please try again.")
                except KeyError as e:
                    st.error(f"Error: Missing or invalid data in question or response - {str(e)}.")
                except ValueError as e:
                    st.error(f"Error: Invalid response format - {str(e)}.")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {str(e)}. Please try again.")
    else:
        st.error("Error: No current revision question available.")

    # if not st.session_state["revision_questions"]:
    #     st.session_state["learning_mode"] = False
    #     st.session_state["current_revision_question"] = None
    #     st.session_state["guide_text"] = None
    #     st.session_state["weak_topics"] = []
    #     st.button("Start Next Level Quiz")
