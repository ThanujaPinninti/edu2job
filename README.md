# EDU2JOB – Intelligent Career Prediction System
EDU2JOB is a web-based intelligent career prediction system that recommends suitable job roles based on a user’s educational background, academic performance, skills, and certifications using Machine Learning. The system also provides career insights, visualizations, user feedback, and an admin dashboard for model management.

---

## Features
- Secure User Registration & Login  
- Career Prediction using Machine Learning  
- Top Job Role Recommendations with Confidence Scores  
- Interactive Career Visualizations (Charts & Insights)  
- Prediction History & User Feedback  
- Admin Dashboard for Dataset Upload & Model Retraining  
- Modular and Scalable Architecture  

---

## Technology Stack
### Frontend
- HTML  
- CSS  
- JavaScript  
- Chart.js  

### Backend
- Python  
- Flask (REST APIs)  

### Machine Learning
- pandas  
- scikit-learn  
- joblib  

### Database
- MySQL  

### Version Control
- Git & GitHub  

---

## System Architecture
- Frontend handles user interaction and visualization  
- Backend processes requests and manages authentication  
- Machine Learning model predicts suitable job roles  
- Database stores user data, prediction history, and feedback  
- Admin module manages datasets and model retraining  

---

## Workflow
1. User registers and logs in  
2. User enters education and skill details  
3. Data is preprocessed and passed to the ML model  
4. Job roles are predicted and ranked  
5. Results and visualizations are displayed  
6. User provides feedback  
7. Admin reviews logs and retrains the model  

---

## Machine Learning Model
- Algorithm: Random Forest Classifier  
- Input Features: Degree, Specialization, CGPA, Skills, Certifications  
- Output: Ranked Job Role Predictions  
- Model Serialization: joblib  

---

## Installation & Setup
1. Clone the repository
git clone <your-github-repo-link>
2.Navigate to the project directory
cd EDU2JOB
3.Install required dependencies
pip install -r requirements.txt
4.Configure database credentials in the configuration file
5.Run the Flask application
python app.py
6.Open the application in browser
http://localhost:5000

---

## Admin Functionalities
- Upload training datasets
- Retrain Machine Learning model
- View prediction logs
- Analyze user feedback

---

 ## Feedback
- Users can rate the relevance and accuracy of predicted job roles and provide comments.
- This feedback is stored and analyzed to improve model performance.

---

## Future Enhancements
- Real-time job market integration
- Skill gap analysis and learning recommendations
- Resume parsing using NLP
- Mobile application support

---

## Repository Structure
/frontend – User Interface files
/backend – Flask API code
/ml – Machine Learning scripts and models
/database – SQL scripts
/uploads – Uploaded datasets
/logs – Prediction logs

---

## License
This project is developed for academic and learning purposes only.


