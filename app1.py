import streamlit as st
import pandas as pd
import base64
import time
import datetime
import string  # Importing string module for punctuation removal
from fpdf import FPDF
import os


# Libraries to parse the resume pdf files
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
import io
import random
from streamlit_tags import st_tags
from PIL import Image

# Importing custom course data and NLTK
from Courses import ds_course, web_course, android_course, ios_course, uiux_course, resume_videos, interview_videos
import nltk

nltk.download('stopwords')
nltk.download('punkt')

def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            print(page)
        text = fake_file_handle.getvalue()

    # close open handles
    converter.close()
    fake_file_handle.close()
    return text

def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def course_recommender(course_list):
    st.subheader("Courses & Certificates Recommendations")
    c = 0
    rec_course = []
    no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 5)
    random.shuffle(course_list)
    for c_name, c_link in course_list:
        c += 1
        st.markdown(f"({c}) [{c_name}]({c_link})")
        rec_course.append(c_name)
        if c == no_of_reco:
            break
    return rec_course

def preprocess_text(text):
    # Tokenize the text
    tokens = nltk.word_tokenize(text.lower())
    
    # Remove stopwords and punctuation
    stop_words = set(nltk.corpus.stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words and word not in string.punctuation]
    
    # Join tokens back into text
    preprocessed_text = ' '.join(tokens)
    
    return preprocessed_text

def predict_sentiment(text):
    # Preprocess the text
    preprocessed_text = preprocess_text(text)
    
    # Define positive and negative words
    positive_words = ['good', 'great', 'excellent', 'positive', 'awesome']
    negative_words = ['bad', 'poor', 'negative', 'terrible', 'awful']
    
    # Count positive and negative words
    num_positive_words = sum(1 for word in positive_words if word in preprocessed_text)
    num_negative_words = sum(1 for word in negative_words if word in preprocessed_text)
    
    # Determine sentiment based on word counts
    if num_positive_words > num_negative_words:
        return "Positive"
    elif num_negative_words > num_positive_words:
        return "Negative"
    else:
        return "Neutral"

st.set_page_config(
    page_title="Resume Analyzer",
    # page_icon='./NewLogo/logo.png',
)

def suggest_job_roles(keywords):
    # Define lists of job roles based on keywords
    job_roles = {
        'Data Science': ['Data Scientist', 'Machine Learning Engineer', 'Data Analyst'],
        'Web Development': ['Web Developer', 'Frontend Developer', 'Backend Developer'],
        'Android Development': ['Android Developer', 'Mobile App Developer'],
        'iOS Development': ['iOS Developer', 'Mobile App Developer'],
        'UI/UX Development': ['UI/UX Designer', 'User Interface Designer', 'User Experience Designer']
    }
    
    # Initialize lists to store matched job roles
    matched_job_roles = []
    
    # Match keywords with predefined lists of job roles
    for field, roles in job_roles.items():
        for role in roles:
            if any(keyword.lower() in role.lower() for keyword in keywords):
                matched_job_roles.append(role)
    
    # Remove duplicates from the list
    matched_job_roles = list(set(matched_job_roles))
    
    return matched_job_roles



def suggest_interest_areas():
    # Define all possible interest areas
    all_interest_areas = ['Data Science', 'Web Development', 'Android Development', 'iOS Development', 'UI/UX Development']
    return all_interest_areas


def suggest_project_ideas(area):
    projects = []

    # Define project ideas for each interest area
    projects_by_area = {
        'Data Science': ['Predictive Modeling with Python', 'Customer Segmentation Analysis', 'Stock Price Prediction Project'],
        'Web Development': ['Build a Portfolio Website', 'Create a Blogging Platform with Django', 'Develop an E-commerce Website'],
        'Android Development': ['Build a Task Manager App', 'Create a Weather Forecasting App', 'Develop a Budget Tracker App'],
        'iOS Development': ['Develop a Recipe Sharing App', 'Build a Fitness Tracking App', 'Create a To-Do List App'],
        'UI/UX Development': ['Design a User-friendly Dashboard Interface', 'Create Wireframes for an E-commerce Platform', 'Develop a Mobile App Prototype']
    }

    # Retrieve project ideas for the chosen area
    if area in projects_by_area:
        projects = projects_by_area[area]

    return projects


def run():
    st.title("Resume Analyzer")
    st.markdown('<h5 style="color: gray;">Upload your resume, and get smart recommendations</h5>', unsafe_allow_html=True)
    pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
    if pdf_file is not None:
        save_pdf_path = "/tmp/resume_analysis.pdf"  # Path to save the PDF file
        with open(save_pdf_path, "wb") as f:
            f.write(pdf_file.getbuffer())
        show_pdf(save_pdf_path)
        resume_data = ResumeParser(save_pdf_path).get_extracted_data()
        if resume_data:
            ## Get the whole resume data
            resume_text = pdf_reader(save_pdf_path)

            st.header("Resume Analysis")
            st.success("Hello "+ resume_data['name'])
            st.subheader("Your Basic info")
            try:
                st.text('Name: '+resume_data['name'])
                st.text('Email: ' + resume_data['email'])
                st.text('Contact: ' + resume_data['mobile_number'])
                st.text('Resume pages: '+str(resume_data['no_of_pages']))
            except:
                pass
            cand_level = ''
            if resume_data['no_of_pages'] == 1:
                cand_level = "Fresher"
                st.markdown('<h4 class="level-text">You are at Fresher level!</h4>',unsafe_allow_html=True)
            elif resume_data['no_of_pages'] == 2:
                cand_level = "Intermediate"
                st.markdown('<h4 class="level-text">You are at intermediate level!</h4>',unsafe_allow_html=True)
            elif resume_data['no_of_pages'] >=3:
                cand_level = "Experienced"
                st.markdown('<h4 class="level-text">You are at experience level!</h4>',unsafe_allow_html=True)

            ## Skill shows
            keywords = st_tags(label='Your Current Skills',
                                # text='See our skills recommendation below',
                                value=resume_data['skills'],key = '1')

            ##  keywords
            ds_keyword = ['tensorflow','keras','pytorch','machine learning','deep Learning','flask','streamlit']
            web_keyword = ['react', 'django', 'node jS', 'react js', 'php', 'laravel', 'magento', 'wordpress',
                           'javascript', 'angular js', 'c#', 'flask']
            android_keyword = ['android','android development','flutter','kotlin','xml','kivy']
            ios_keyword = ['ios','ios development','swift','cocoa','cocoa touch','xcode']
            uiux_keyword = ['ux','adobe xd','figma','zeplin','balsamiq','ui','prototyping','wireframes','storyframes','adobe photoshop','photoshop','editing','adobe illustrator','illustrator','adobe after effects','after effects','adobe premier pro','premier pro','adobe indesign','indesign','wireframe','solid','grasp','user research','user experience']

            recommended_skills = []
            reco_field = ''
            rec_course = ''
            ## Courses recommendation
            for i in resume_data['skills']:
                ## Data science recommendation
                if i.lower() in ds_keyword:
                    reco_field = 'Data Science'
                    # st.success("Our analysis says you are looking for Data Science Jobs.")
                    recommended_skills = ['Data Visualization','Predictive Analysis','Statistical Modeling','Data Mining','Clustering & Classification','Data Analytics','Quantitative Analysis','Web Scraping','ML Algorithms','Keras','Pytorch','Probability','Scikit-learn','Tensorflow',"Flask",'Streamlit']
                    recommended_keywords = st_tags(label='Recommended skills for you.',
                                                    text='Recommended skills generated from System',value=recommended_skills,key = '2')
                    # st.markdown('<h4 class="reco-text">Adding this skills to resume will boost the chances of getting a Job</h4>',unsafe_allow_html=True)
                    rec_course = course_recommender(ds_course)
                    break

                ## Web development recommendation
                elif i.lower() in web_keyword:
                    reco_field = 'Web Development'
                    # st.success("Our analysis says you are looking for Web Development Jobs")
                    recommended_skills = ['React','Django','Node JS','React JS','php','laravel','Magento','wordpress','Javascript','Angular JS','c#','Flask','SDK']
                    recommended_keywords = st_tags(label='Recommended skills for you.',
                                                    text='Recommended skills generated from System',value=recommended_skills,key = '3')
                    # st.markdown('<h4 class="reco-text">Adding this skills to resume will boost the chances of getting a Job</h4>',unsafe_allow_html=True)
                    rec_course = course_recommender(web_course)
                    break

                ## Android App Development
                elif i.lower() in android_keyword:
                    reco_field = 'Android Development'
                    # st.success("Our analysis says you are looking for Android App Development Jobs")
                    recommended_skills = ['Android','Android development','Flutter','Kotlin','XML','Java','Kivy','GIT','SDK','SQLite']
                    recommended_keywords = st_tags(label='Recommended skills for you.',
                                                    text='Recommended skills generated from System',value=recommended_skills,key = '4')
                    # st.markdown('<h4 class="reco-text">Adding this skills to resume will boost the chances of getting a Job</h4>',unsafe_allow_html=True)
                    rec_course = course_recommender(android_course)
                    break

                ## IOS App Development
                elif i.lower() in ios_keyword:
                    reco_field = 'IOS Development'
                    # st.success("Our analysis says you are looking for IOS App Development Jobs")
                    recommended_skills = ['IOS','IOS Development','Swift','Cocoa','Cocoa Touch','Xcode','Objective-C','SQLite','Plist','StoreKit',"UI-Kit",'AV Foundation','Auto-Layout']
                    recommended_keywords = st_tags(label='Recommended skills for you.',
                                                    text='Recommended skills generated from System',value=recommended_skills,key = '5')
                    # st.markdown('<h4 class="reco-text">Adding this skills to resume will boost the chances of getting a Job</h4>',unsafe_allow_html=True)
                    rec_course = course_recommender(ios_course)
                    break

                ## Ui-UX Recommendation
                elif i.lower() in uiux_keyword:
                    reco_field = 'UI-UX Development'
                    # st.success("Our analysis says you are looking for UI-UX Development Jobs")
                    recommended_skills = ['UI','User Experience','Adobe XD','Figma','Zeplin','Balsamiq','Prototyping','Wireframes','Storyframes','Adobe Photoshop','Editing','Illustrator','After Effects','Premier Pro','Indesign','Wireframe','Solid','Grasp','User Research']
                    recommended_keywords = st_tags(label='Recommended skills for you.',
                                                    text='Recommended skills generated from System',value=recommended_skills,key = '6')
                    # st.markdown('<h4 class="reco-text">Adding this skills to resume will boost the chances of getting a Job</h4>',unsafe_allow_html=True)
                    rec_course = course_recommender(uiux_course)
                    break

            ### Resume writing recommendation
            st.subheader("Resume Tips & Ideas")
            resume_score = 0
            if 'Objective' in resume_text:
                resume_score = resume_score+20
                st.markdown('<h5 class="tip-text">[+] Awesome! You have added Objective</h5>',unsafe_allow_html=True)
            else:
                st.markdown('<h5 class="tip-text">[-] Please add your career objective, it will give your career intension to the Recruiters.</h5>',unsafe_allow_html=True)

            if 'Declaration'  in resume_text:
                resume_score = resume_score + 20
                st.markdown('<h5 class="tip-text">[+] Awesome! You have added Delcaration</h5>',unsafe_allow_html=True)
            else:
                st.markdown('<h5 class="tip-text">[-] Please add Declaration. It will give the assurance that everything written on your resume is true and fully acknowledged by you</h5>',unsafe_allow_html=True)

            if 'Hobbies' or 'Interests'in resume_text:
                resume_score = resume_score + 20
                st.markdown('<h5 class="tip-text">[+] Awesome! You have added your Hobbies</h5>',unsafe_allow_html=True)
            else:
                st.markdown('<h5 class="tip-text">[-] Please add Hobbies. It will show your persnality to the Recruiters and give the assurance that you are fit for this role or not.</h5>',unsafe_allow_html=True)

            if 'Achievements' in resume_text:
                resume_score = resume_score + 20
                st.markdown('<h5 class="tip-text">[+] Awesome! You have added your Achievements </h5>',unsafe_allow_html=True)
            else:
                st.markdown('<h5 class="tip-text">[-] Please add Achievements. It will show that you are capable for the required position.</h5>',unsafe_allow_html=True)

            if 'Projects' in resume_text:
                resume_score = resume_score + 20
                st.markdown('<h5 class="tip-text">[+] Awesome! You have added your Projects</h5>',unsafe_allow_html=True)
            else:
                st.markdown('<h5 class="tip-text">[-] Please add Projects. It will show that you have done work related the required position or not.</h5>',unsafe_allow_html=True)

            # Sentiment analysis
            resume_sentiment = predict_sentiment(resume_text)
            st.subheader("Resume Sentiment Analysis")
            st.write("Overall Sentiment:", resume_sentiment)

            ### Resume writing recommendation based on sentiment score
            if resume_sentiment == "Positive":
                st.success("Your resume has a positive sentiment. Great job! Here are some personalized points:")
                st.markdown("- Your resume reflects a positive attitude, which is attractive to employers.")
                st.markdown("- Highlight your accomplishments and skills even more to stand out.")
            elif resume_sentiment == "Neutral":
                st.info("Your resume sentiment is neutral. Consider these personalized points:")
                st.markdown("- Add more quantifiable achievements to demonstrate your impact.")
                st.markdown("- Tailor your resume to the specific job roles you're applying for.")
            else:
                st.error("Your resume has a negative sentiment. Here are some personalized points to improve:")
                st.markdown("- Focus on showcasing your achievements and skills more prominently.")
                st.markdown("- Proofread your resume thoroughly for language and formatting errors.")

            ### Suggest job roles based on keywords
            suggested_roles = suggest_job_roles(resume_data['skills'])
            if suggested_roles:
                st.subheader("Suggested Job Roles")
                for role in suggested_roles:
                    st.write(role)


            st.subheader("Project Ideas")


            interest_areas = suggest_interest_areas()
            if interest_areas:
                chosen_area = st.selectbox("Select the area you're interested in:", interest_areas)
                st.subheader(f"Project Ideas for {chosen_area}")
                project_ideas = suggest_project_ideas(chosen_area)
                if project_ideas:
                    for project in project_ideas:
                        st.write("- ", project)
                else:
                    st.info("No specific project ideas available for this area.")
            else:
                st.info("No interest areas available.")

            
        else:
            st.error('Something went wrong..')

run()

