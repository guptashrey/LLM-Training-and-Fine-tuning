# library imports
from haystack.nodes import PreProcessor, DensePassageRetriever
from haystack import Document

import pandas as pd
import os
import texthero as hero
import logging
import glob
import argparse

logging.getLogger("haystack").setLevel(logging.ERROR)
logger = logging.getLogger("Add Data to ES")
logger.setLevel(logging.INFO)

from helper_functions import get_elasticsearch_document_store

def initialize():
    """
    Initialize ElasticsearchDocumentStore and DensePassageRetriever for use in the pipeline.

    Args:
        None
    
    Return:
        document_store: ElasticsearchDocumentStore
        retriever: DensePassageRetriever
    """

    # get the host where Elasticsearch is running, default to localhost
    host = os.environ.get("ELASTICSEARCH_HOST", "localhost")

    # get ElasticsearchDocumentStore
    document_store = get_elasticsearch_document_store(host, "document1")
    logger.info("Created ElasticsearchDocumentStore")

    # initialize retriever model for creating embeddings
    retriever = DensePassageRetriever(
        document_store=document_store,
        query_embedding_model="facebook/dpr-question_encoder-single-nq-base",
        passage_embedding_model="facebook/dpr-ctx_encoder-single-nq-base"
    )
    logger.info("Retriever model initialized")

    return document_store, retriever

def index_in_es(data_directory):
    '''
    Process the webpages text data and index them in Elasticsearch.

    Args:
        None
    
    Return:
        None
    '''

    # load list of scraped websites
    sites = glob.glob(data_directory + "/*/", recursive=False)
    sites.sort()

    # create list of files to read across all websites
    file_list_all = []
    for site in sites:
        file_list_level1 = glob.glob(f"{site}*.txt", recursive=False)
        file_list_level2 = glob.glob(f"{site}*/*.txt", recursive=False)
        file_list_level3 = glob.glob(f"{site}*/*/*.txt", recursive=False)
        file_list_level4 = glob.glob(f"{site}*/*/*/*.txt", recursive=False)
        file_list_level5 = glob.glob(f"{site}*/*/*/*/*.txt", recursive=False)
        file_list_level6 = glob.glob(f"{site}*/*/*/*/*/*.txt", recursive=False)
        file_list_all.extend(file_list_level1)
        file_list_all.extend(file_list_level2)
        file_list_all.extend(file_list_level3)
        file_list_all.extend(file_list_level4)
        file_list_all.extend(file_list_level5)
        file_list_all.extend(file_list_level6)

    # read in all files
    i = 0
    for file in file_list_all:
        with open(file) as f:
                text = f.read()
        if i == 0:
            temp = pd.DataFrame({"text": [text]})
        else:
            temp = pd.concat([temp, pd.DataFrame({"text": [text]})])
        i += 1
    logger.info("Read in all files completed")

    # clean data
    custom_pipeline = [hero.preprocessing.remove_whitespace,
                    hero.preprocessing.remove_angle_brackets,
                    hero.preprocessing.remove_html_tags,
                    hero.preprocessing.remove_urls]
    
    temp["cleaned_text"] = hero.clean(temp["text"], custom_pipeline)

    # replace websites header and footer
    text_to_replace = ["© Copyright 2011-2023 Duke University * __Main Menu * __Why Duke? * __The Duke Difference * __Career Services * __Graduate Outcomes * __What Tech Leaders Are Saying * __Degree * __Courses * __Faculty * __Advisory Board * __Apply * __Quick Links * __News * __Events * __Steering Committee * __Contact *",
                   "Jump to navigation * Duke Engineering * Pratt School of Engineering * Institute for Enterprise Engineering * News * Events * Steering Committee * Contact __ * Why Duke? * The Duke Difference * Career Services * Graduate Outcomes * What Tech Leaders Are Saying * Degree * Courses * Faculty * Advisory Board * Apply __",
                   "Skip to main content * Departments & Centers * Overview * Biomedical Engineering * Civil & Environmental Engineering * Electrical & Computer Engineering * Mechanical Engineering & Materials Science * Institute for Enterprise Engineering * Alumni & Parents * Overview * Alumni * Parents * Giving * Board of Visitors * Our History * Email Newsletter * Meet the Team * Corporate Partners * Overview * Partners & Sponsors * Data Science & AI Industry Affiliates * Connect With Students * Recruiting Our Students * Sponsored Research * TechConnect Career Networking * Apply * Careers * Directory * Undergraduate * 1. For Prospective Students 1. Majors & Minors 2. Certificates 3. General Degree Requirements 4. 4+1: BSE+Master's Degree 5. Campus Tours 6. How to Apply 2. First-Year Design 3. Student Entrepreneurship 4. Undergraduate Research 5. Where Our Undergrads Go 6. Diversity, Equity & Inclusion 7. For Current Students 1. The First Year 2. Advising 3. Student Clubs & Teams 4. Graduation with Distinction 5. Internships 6. Policies & Procedures * Graduate * 1. For Prospective Students 1. PhD Programs 2. Master's Degrees 3. Online Specializations, Certificates and Short Courses 4. Admissions Events 5. How to Apply 2. For Admitted Students 3. Diversity, Equity & Inclusion 1. Bootcamp for Applicants 2. Recruiting Incentives 4. For Current Grad Students 1. Graduate Student Programs & Services * Faculty & Research * 1. Faculty 1. Faculty Profiles 2. New Faculty 3. Awards and Recognition 4. NAE Members 2. Research 1. Signature Research Themes 2. Recent External Funding Awards 3. Faculty Entrepreneurship 4. Duke Engineering Discoveries * About * 1. Dean's Welcome 2. Campus & Tours 3. Facts & Rankings 4. Diversity, Equity & Inclusion 5. Service to Society 6. Entrepreneurship 7. Governance 8. News & Media 1. Latest News 2. Podcast 3. Email Newsletter 4. Publications 5. Media Coverage 6. Public Health Information 9. Events 1. Events Calendar 2. Academic Calendar 3. Commencement 10. Art @ Duke Engineering",
                   "Skip to main content * Duke University » * Pratt School of Engineering » ## Secondary Menu * Apply * Careers * Contact * Undergraduate * 1. Admissions 1. Degree Program 2. Enrollment and Graduation Rates 3. Career Outcomes 4. Campus Tours 5. How to Apply 2. Academics 1. Curriculum 2. Double Majors 3. BME Design Fellows 3. Student Resources 1. For Current Students 2. 4+1: BSE+Master's Degree * Master's * 1. Admissions 1. Degree Programs 2. Career Outcomes 3. How to Apply 2. Academics 1. Courses 2. Concentrations 3. Certificates 3. Student Resources 1. For Current Students * PhD * 1. Admissions 1. PhD Program 2. Meet Our Students 3. Career Outcomes 4. How to Apply 2. Academics 1. Courses 2. Certificates & Training Programs 3. Student Resources 1. For Current Students * Research * 1. Major Research Programs 2. Centers & Initiatives 3. Research News * Faculty * 1. Faculty Profiles 2. Awards & Recognition * Coulter * 1. The Duke-Coulter Partnership 2. Proposal Process 3. Project Archive 4. Oversight Committee 5. FAQs * About * 1. Welcome from the Chair 2. Vision & Mission 3. Facts & Stats 4. Serving Society 5. News 1. Media Coverage 2. Duke BME Magazine 3. Email Newsletter 6. Events 1. Seminars 7. Our History 8. Driving Directions",
                   "Jump to navigation * Duke Engineering * Pratt School of Engineering * Institute for Enterprise Engineering * Industry Relations * Leadership * News * Contact __ * Why Duke? * The Duke Difference * Career Services * Graduate Outcomes * What Tech Leaders Are Saying * Degree * Certificate * Courses * Faculty * Apply",
                   "# Page Not Found We're sorry, but that page was not found. Please check the spelling of the page address or search this website. * * * * * © Copyright 2011-2023 Duke University drupal_block( 'search_form_block', { label_display: false } ) * Undergraduate * Admissions * Degree Program * Enrollment and Graduation Rates * Career Outcomes * Campus Tours * How to Apply * Academics * Curriculum * Double Majors * BME Design Fellows * Student Resources * For Current Students * 4+1: BSE+Master's Degree * Master's * Admissions * Degree Programs * Career Outcomes * How to Apply * Academics * Courses * Concentrations * Certificates * Student Resources * For Current Students * PhD * Admissions * PhD Program * Meet Our Students * Career Outcomes * How to Apply * Academics * Courses * Certificates & Training Programs * Student Resources * For Current Students * Research * Major Research Programs * Centers & Initiatives * Research News * Faculty * Faculty Profiles * Awards & Recognition * Coulter * The Duke-Coulter Partnership * Proposal Process * Project Archive * Oversight Committee * FAQs * About * Welcome from the Chair * Vision & Mission * Facts & Stats * Serving Society * News * Media Coverage * Duke BME Magazine * Email Newsletter * Events * Seminars * Past Seminars * Our History * Driving Directions",
                   "Skip to main content * Departments & Centers * Overview * Biomedical Engineering * Civil & Environmental Engineering * Electrical & Computer Engineering * Mechanical Engineering & Materials Science * Institute for Enterprise Engineering * Alumni & Parents * Overview * Alumni * Parents * Giving * Board of Visitors * Our History * Email Newsletter * Meet the Team * Corporate Partners * Overview * Partners & Sponsors * Data Science & AI Industry Affiliates * Connect With Students * Recruiting Our Students * Sponsored Research * TechConnect Career Networking * Apply * Careers * Directory * Undergraduate * 1. For Prospective Students 1. Majors & Minors 2. Certificates 3. General Degree Requirements 4. 4+1: BSE+Master's Degree 5. Campus Tours 6. How to Apply 2. First-Year Design 3. Student Entrepreneurship 4. Undergraduate Research 5. Where Our Undergrads Go 6. Diversity, Equity & Inclusion 7. For Current Students 1. The First Year 2. Advising 3. Student Clubs & Teams 4. Graduation with Distinction 5. Internships 6. Policies & Procedures * Graduate * 1. For Prospective Students 1. PhD Programs 2. Master's Degrees 3. Online Specializations, Certificates and Short Courses 4. Admissions Events 5. How to Apply 2. For Admitted Students 3. Diversity, Equity & Inclusion 1. Bootcamp for Applicants 2. Recruiting Incentives 4. For Current Grad Students 1. Graduate Student Programs & Services * Faculty & Research * 1. Faculty 1. Faculty Profiles 2. New Faculty 3. Awards and Recognition 4. NAE Members 2. Research 1. Signature Research Themes 2. Recent External Funding Awards 3. Faculty Entrepreneurship 4. Duke Engineering Discoveries * About * 1. Dean's Welcome 2. Campus & Tours 3. Facts & Rankings 4. Diversity, Equity & Inclusion 5. Service to Society 6. Entrepreneurship 7. Governance 8. News & Media 1. Latest News 2. Podcast 3. Email Newsletter 4. Publications 5. Media Coverage 6. Public Health Information 9. Events 1. Events Calendar 2. Academic Calendar 3. Commencement 10. Art @ Duke Engineering ## You are here Home » About » News & Media",
                   "Skip to main content * Duke University » * Pratt School of Engineering » ## Secondary Menu * Apply * Careers * Contact * Undergraduate * 1. The Duke Difference 1. Why Duke for CEE? 2. Enrollment and Graduation Rates 3. Where Our Students Go 2. Degree Options 1. Civil Eng Degree Planning 2. Civil Eng Study Tracks 3. Env. Eng Degree Planning 4. Dual Majors 5. Certificates 6. 4+1: BSE+Master's 3. For Current Students 1. Courses 2. Research & Independent Study 3. Outreach & Service Learning 4. Senior Design Capstone 5. Internships & Career Planning 6. Graduation with Distinction * Graduate * 1. The Duke Difference 1. Degree Options 2. Scholarships & Financial Support 3. Graduate Study Tracks 4. Graduate Certificates 5. Course Descriptions 2. Master's Study 1. Master of Science in CEE 2. Civil Engineering 3. Computational Mechanics and Scientfic Computing 4. Environmental Engineering 5. Risk Engineering 6. Career Services 7. Career Outcomes 3. PhD 1. Meet Our Students 2. PhD Career Outcomes 4. For Current Students * Research * 1. Overview 2. Research News 3. Computational Mechanics & Scientific Computing 4. Environmental Health Engineering 5. Geomechanics & Geophysics for Energy and the Environment 6. Hydrology & Fluid Dynamics 7. Risk & Resilient Systems * Faculty * 1. Faculty Profiles 2. Awards & Recognition * About * 1. Facts & Stats 2. Meet the Chair 3. Serving a Global Society 4. Advisory Board 5. Alumni 6. Awards & Honors 7. News 1. Media Coverage 2. Email Newsletter 3. Duke CEE Magazine 8. Events 1. Seminars",
                   "# Page Not Found We're sorry, but that page was not found. Please check the spelling of the page address or search this website. * * * * * © Copyright 2011-2023 Duke University drupal_block( 'search_form_block', { label_display: false } ) * Undergraduate * The Duke Difference * Why Duke for CEE? * Enrollment and Graduation Rates * Where Our Students Go * Degree Options * Civil Eng Degree Planning * Civil Eng Study Tracks * Env. Eng Degree Planning * Dual Majors * Certificates * Architectural Engineering * Global Development * Energy & The Environment * 4+1: BSE+Master's * For Current Students * Courses * Research & Independent Study * Outreach & Service Learning * Senior Design Capstone * Internships & Career Planning * Graduation with Distinction * Graduate * The Duke Difference * Degree Options * Scholarships & Financial Support * Graduate Study Tracks * Graduate Certificates * Course Descriptions * Master's Study * Master of Science in CEE * Civil Engineering * Computational Mechanics and Scientfic Computing * Environmental Engineering * Risk Engineering * Career Services * Career Outcomes * PhD * Meet Our Students * PhD Career Outcomes * For Current Students * Research * Overview * Research News * Computational Mechanics & Scientific Computing * Environmental Health Engineering * Geomechanics & Geophysics for Energy and the Environment * Hydrology & Fluid Dynamics * Risk & Resilient Systems * Faculty * Faculty Profiles * Awards & Recognition * About * Facts & Stats * Meet the Chair * Serving a Global Society * Advisory Board * Alumni * Awards & Honors * News * Media Coverage * Email Newsletter * Duke CEE Magazine * Events * Seminars * Past Seminars",
                   "Copyright 2011-2023 Duke University drupal_block( 'search_form_block', { label_display: false } ) * Undergraduate * The Duke Difference * Why Duke for CEE? * Enrollment and Graduation Rates * Where Our Students Go * Degree Options * Civil Eng Degree Planning * Civil Eng Study Tracks * Env. Eng Degree Planning * Dual Majors * Certificates * Architectural Engineering * Global Development * Energy & The Environment * 4+1: BSE+Master's * For Current Students * Courses * Research & Independent Study * Outreach & Service Learning * Senior Design Capstone * Internships & Career Planning * Graduation with Distinction * Graduate * The Duke Difference * Degree Options * Scholarships & Financial Support * Graduate Study Tracks * Graduate Certificates * Course Descriptions * Master's Study * Master of Science in CEE * Civil Engineering * Computational Mechanics and Scientfic Computing * Environmental Engineering * Risk Engineering * Career Services * Career Outcomes * PhD * Meet Our Students * PhD Career Outcomes * For Current Students * Research * Overview * Research News * Computational Mechanics & Scientific Computing * Environmental Health Engineering * Geomechanics & Geophysics for Energy and the Environment * Hydrology & Fluid Dynamics * Risk & Resilient Systems * Faculty * Faculty Profiles * Awards & Recognition * About * Facts & Stats * Meet the Chair * Serving a Global Society * Advisory Board * Alumni * Awards & Honors * News * Media Coverage * Email Newsletter * Duke CEE Magazine * Events * Seminars * Past Seminars",
                   "Page Not Found We're sorry, but that page was not found. Please check the spelling of the page address or search this website. * * * * * © Copyright 2011-2023 Duke University drupal_block( 'search_form_block', { label_display: false } ) * Undergraduate * Overview * Degree Programs * BSE Degree Planning * Areas of Concentration * Concentration in Machine Learning * Minor in ECE * Minor in Machine Learning & AI * For Applicants * Enrollment and Graduation Rates * Where Our Students Go * What's the difference between CS and ECE? * For Current Students * Courses * Innovations in Remote Learning * Independent Study * Senior Design * Graduation with Distinction * Awards and Honors * Research Experiences for Undergrads (REU) * Master's * Overview * Degree Options * Master of Science (MS) * Master of Engineering (MEng) * Areas of Study * Software Development * Hardware Design * Data Analytics & Machine Learning * Quantum Computing * Microelectronics, Photonics & Nanotechnology * Design Your Own ECE Degree * Master's Admissions * Master's Career Outcomes * Life at Duke * Research Opportunities * Graduate Courses * Online Courses * PhD * Overview * Degree Requirements * Academic Curricular Groups * PhD Admissions * Promoting an Inclusive Environment * Meet Our Students * PhD Awards and Honors * PhD Career Outcomes * Certificates & Training Programs * Graduate Courses * DEEP SEA Startup Accelerator * Career & Professional Services * Faculty & Research * Overview * AI/Machine Learning * Metamaterials * Quantum Computing * Nanoelectronic Materials & Devices * Sensing & Imaging * Trustworthy Computing * Faculty Profiles * Awards & Recognition * Research News * Ask an Expert * About * From the Chair * News * Media Coverage * Email Newsletter * Duke ECE Magazine * Events * Distinguished Speaker Series * Seminars * Past Seminars * Facts & Stats * Mission & Vision * Diversity, Equity, Inclusion & Community * Entrepreneurship Success Stories * Meet Our Alumni * Industry Advisory Board",
                   "Skip to main content * Duke University » * Pratt School of Engineering » ## Secondary Menu * Apply * Careers * Contact * Undergraduate * 1. Overview 2. Degree Programs 1. BSE Degree Planning 2. Areas of Concentration 3. Concentration in Machine Learning 4. Minor in ECE 5. Minor in Machine Learning & AI 3. For Applicants 1. Enrollment and Graduation Rates 2. Where Our Students Go 3. What's the difference between CS and ECE? 4. For Current Students 1. Courses 2. Innovations in Remote Learning 3. Independent Study 4. Senior Design 5. Graduation with Distinction 6. Awards and Honors 5. Research Experiences for Undergrads (REU) * Master's * 1. Overview 2. Degree Options 1. Master of Science (MS) 2. Master of Engineering (MEng) 3. Areas of Study 1. Software Development 2. Hardware Design 3. Data Analytics & Machine Learning 4. Quantum Computing 5. Microelectronics, Photonics & Nanotechnology 6. Design Your Own ECE Degree 4. Master's Admissions 5. Master's Career Outcomes 6. Life at Duke 7. Research Opportunities 8. Graduate Courses 9. Online Courses * PhD * 1. Overview 2. Degree Requirements 3. Academic Curricular Groups 4. PhD Admissions 5. Promoting an Inclusive Environment 6. Meet Our Students 1. PhD Awards and Honors 7. PhD Career Outcomes 8. Certificates & Training Programs 9. Graduate Courses 10. DEEP SEA Startup Accelerator 11. Career & Professional Services * Faculty & Research * 1. Overview 1. AI/Machine Learning 2. Metamaterials 3. Quantum Computing 4. Nanoelectronic Materials & Devices 5. Sensing & Imaging 6. Trustworthy Computing 2. Faculty Profiles 3. Awards & Recognition 4. Research News 5. Ask an Expert * About * 1. From the Chair 2. News 1. Media Coverage 2. Email Newsletter 3. Duke ECE Magazine 3. Events 1. Distinguished Speaker Series 2. Seminars 4. Facts & Stats 5. Mission & Vision 6. Diversity, Equity, Inclusion & Community 7. Entrepreneurship Success Stories 8. Meet Our Alumni 9. Industry Advisory Board",
                   "© Copyright 2011-2023 Duke University * __Main Menu * __Why Duke? * __On-Campus * __Duke MEM On-Campus * __Curriculum * __Curriculum Overview * __Seminar & Workshop Series * __Required Internship * __Consulting Practicum * __Elective Tracks * __Course Descriptions * __Flexible Degree Options * __Student Services and Support * __Career Outcomes * __Meet Our Alumni * __Tuition and Financial Aid * __External Funding Opportunities * __Online * __Duke MEM Online * __Boeing-Learning Together * __Curriculum * __Elective Tracks * __Residencies * __Course Descriptions * __Previous Courses * __Student Services and Support * __Meet Our Alumni * __Tuition and Financial Aid * __Certificate * __Apply * __Apply to Duke * __Application Requirements * __The 5 Principles * __Quick Links * __Directory * __Industry * __Alumni * __News * __Students * __Contact *",
                   "Jump to navigation * Duke Engineering * Pratt School of Engineering * Institute for Enterprise Engineering * Directory * Industry * Alumni * News * Students * Contact __ * Why Duke? * On-Campus * Duke MEM On-Campus * Curriculum * Elective Tracks * Course Descriptions * Flexible Degree Options * Student Services and Support * Career Outcomes * Meet Our Alumni * Tuition and Financial Aid * Online * Duke MEM Online * Boeing-Learning Together * Curriculum * Elective Tracks * Residencies * Course Descriptions * Student Services and Support * Meet Our Alumni * Tuition and Financial Aid * Certificate * Apply * Apply to Duke * Application Requirements * The 5 Principles __",
                   "Skip to main content * Duke University » * Pratt School of Engineering » ## Secondary Menu * Apply * Careers * Contact * Undergraduate * 1. Overview 2. Degree Programs 1. BSE Degree Planning 2. ME/BME Double Major 3. Certificates 4. 4+1: BSE+Master's 5. Courses 3. For Applicants 1. Why Duke MEMS? 2. Where Our Students Go 3. Enrollment and Graduation Rates 4. For Current Students 1. Awards & Honors 2. Graduation with Distinction 3. Independent Study 4. Senior Design * Master's * 1. Earn Your Master's at Duke 2. Admissions 3. Degrees 1. Master of Science 2. Master of Engineering 4. Concentrations 5. Certificates 1. Aerospace Graduate Certificate 6. Courses 7. Career Outcomes 8. Life at Duke 9. MEMS Graduate Student Committee * PhD * 1. Earn Your PhD at Duke 2. PhD Admissions 3. Certificates, Fellowships & Training Programs 4. Courses 5. Career Outcomes 6. Meet Our PhD Students 7. MEMS Graduate Student Committee * Research * 1. Overview 2. Aero 3. Autonomy 4. Bio 5. Computing / AI 6. Energy 7. Soft / Nano 8. Research Facilities * Faculty * 1. All Faculty 2. Awards & Recognition * About * 1. Welcome to Duke MEMS 2. Meet the Alstadt Chair 3. Meet the Staff 4. Facts & Stats 5. Diversity, Equity, Inclusion & Community 6. News 1. Media Coverage 2. Email Newsletter 3. Research News 7. All Events 1. Pearsall Lecture Series 2. Seminars 8. Our History 9. Driving Directions",
                   "Page Not Found We're sorry, but that page was not found. Please check the spelling of the page address or search this website. * * * * * © Copyright 2011-2023 Duke University drupal_block( 'search_form_block', { label_display: false } ) * Undergraduate * Overview * Degree Programs * BSE Degree Planning * ME/BME Double Major * Certificates * Aerospace Engineering * Energy & the Environment * Materials Science & Engineering * 4+1: BSE+Master's * Courses * For Applicants * Why Duke MEMS? * Where Our Students Go * Enrollment and Graduation Rates * For Current Students * Awards & Honors * Graduation with Distinction * Independent Study * Senior Design * Master's * Earn Your Master's at Duke * Admissions * Degrees * Master of Science * Master of Engineering * Concentrations * Certificates * Aerospace Graduate Certificate * Courses * Career Outcomes * Life at Duke * MEMS Graduate Student Committee * PhD * Earn Your PhD at Duke * PhD Admissions * Certificates, Fellowships & Training Programs * Courses * Career Outcomes * Meet Our PhD Students * MEMS Graduate Student Committee * Research * Overview * Aero * Autonomy * Bio * Computing / AI * Energy * Soft / Nano * Research Facilities * Faculty * All Faculty * Awards & Recognition * About * Welcome to Duke MEMS * Meet the Alstadt Chair * Meet the Staff * Facts & Stats * Diversity, Equity, Inclusion & Community * News * Media Coverage * Email Newsletter * Research News * All Events * Pearsall Lecture Series * Seminars * Our History * Driving Directions",
                   "© Copyright 2011-2023 Duke University drupal_block( 'search_form_block', { label_display: false } ) * Undergraduate * Overview * Degree Programs * BSE Degree Planning * ME/BME Double Major * Certificates * Aerospace Engineering * Energy & the Environment * Materials Science & Engineering * 4+1: BSE+Master's * Courses * For Applicants * Why Duke MEMS? * Where Our Students Go * Enrollment and Graduation Rates * For Current Students * Awards & Honors * Graduation with Distinction * Independent Study * Senior Design * Master's * Earn Your Master's at Duke * Admissions * Degrees * Master of Science * Master of Engineering * Concentrations * Certificates * Aerospace Graduate Certificate * Courses * Career Outcomes * Life at Duke * MEMS Graduate Student Committee * PhD * Earn Your PhD at Duke * PhD Admissions * Certificates, Fellowships & Training Programs * Courses * Career Outcomes * Meet Our PhD Students * MEMS Graduate Student Committee * Research * Overview * Aero * Autonomy * Bio * Computing / AI * Energy * Soft / Nano * Research Facilities * Faculty * All Faculty * Awards & Recognition * About * Welcome to Duke MEMS * Meet the Alstadt Chair * Meet the Staff * Facts & Stats * Diversity, Equity, Inclusion & Community * News * Media Coverage * Email Newsletter * Research News * All Events * Pearsall Lecture Series * Seminars * Our History * Driving Directions",
                   "Skip to main content * Duke University * Pratt School of Engineering * Apply Online * Visit * Contact __ * About * Is Duke Right for Me? * About the MEng Degree at Duke * Courses and Curriculum * Internship/Project * Career Services & Outcomes * Options for Current Duke Students * Non-Degree Candidates * Apply * How to Apply * Connect With Us * Visit Duke * Application Requirements * Application Deadlines * Apply Online * Tuition and Financial Aid __",
                   "© Copyright 2011-2023 Duke University * __Main Menu * __About * __Is Duke Right for Me? * __About the MEng Degree at Duke * __Courses and Curriculum * __Internship/Project * __Career Services & Outcomes * __Options for Current Duke Students * __Non-Degree Candidates * __Apply * __How to Apply * __Connect With Us * __Visit Duke * __Application Requirements * __Uploading a Transcript * __Grade Scale * __Short Answer Essays * __Resume * __Recommendations * __GRE Scores * __English Language Testing * __Application Fee * __Interview/Video Introduction * __Minimum Application Requirements * __International Applicants * __Deposit for Enrolling Students * __Submitting Final Transcripts * __Application Deadlines * __Apply Online * __Tuition and Financial Aid * __Quick Links * __Apply Online * __Visit * __Contact *"]
    
    for text in text_to_replace:
        temp["cleaned_text"] = temp["cleaned_text"].str.replace(text, "", regex=False)
    logger.info("Data cleaning completed")
    
    print(len(temp))
    temp["special_char_count"] = temp["cleaned_text"].apply(lambda x: x.count("�"))
    temp = temp[temp["special_char_count"] == 0]
    print(len(temp))
    
    # create list of documents for elastic search
    list_of_docs = []
    for index, row in temp.iterrows():
        doc = Document(row["cleaned_text"])
        list_of_docs.append(doc)
    logger.info("List of documents created")

    # initialize haystack preprocessor
    preprocessor = PreProcessor(
        clean_whitespace=True,
        clean_header_footer=True,
        clean_empty_lines=True,
        split_by="word",
        split_length=250,
        split_overlap=10,
        split_respect_sentence_boundary=True
    )

    # split documents into smaller chunks
    preprocessed_docs = preprocessor.process(documents=list_of_docs)
    logger.info("Documents split into smaller chunks")

    # write documents to document store
    document_store.write_documents(preprocessed_docs)
    logger.info("Documents written to document store")

    # update embeddings of documents in the document store using the retriever model
    document_store.update_embeddings(retriever)
    logger.info("Embeddings updated")

if __name__ == "__main__":
    # create parser
    parser = argparse.ArgumentParser(
                    prog='index_in_es',
                    description='This script indexes the text of all the scraped webpages into ElasticSearch')
    parser.add_argument('data_directory', type=str, help='Directory where the scraped webpages are stored')

    # parse arguments
    args = parser.parse_args()
    data_directory = args.data_directory

    document_store, retriever = initialize()
    index_in_es(data_directory)