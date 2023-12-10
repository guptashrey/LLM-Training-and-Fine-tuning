# LLM Training and Fine-Tuning
**Duke AIPI 591 (Independent Study in GenAI) Research Project**

## Project Overview
The aim of this project is to research the different ways in which Large Language Models (LLMs) can be trained and fine-tuned to perform Question Answering (QA) tasks. This project builds upon the [Duke ChatBot](https://github.com/guptashrey/Duke-ChatBot) project and aims to improve the performance of the ChatBot by training and fine-tuning LLMs on the Duke University data.

&nbsp;
## Data Sources

Data about Duke University is needed to power the answers to the questions asked by the users. There is no particular dataset or data source that can be used to get all the information about Duke University. Hence, we need to scrape data from multiple websites and webpages to get the required information.

As there are multiple departments, schools and programs at Duke University, we need to scrape data from multiple subdomains of the main website [duke.edu](https://www.duke.edu/). The following are the subdomains from where the data is being scraped:

* [Master of Engineering in AI](https://ai.meng.duke.edu/)
* [Biomedical Engineering](https://bme.duke.edu/)
* [Civil & Environmental Engineering](https://cee.duke.edu/)
* [Master of Engineering in Cybersecurity](https://cybersecurity.meng.duke.edu)
* [Electrical & Computer Engineering](https://www.ece.duke.edu/)
* [Master of Engineering Management](https://memp.pratt.duke.edu/)
* [Mechanical Engineering & Materials Science](https://mems.duke.edu/)
* [Master of Engineering](https://meng.pratt.duke.edu/)
* [Pratt School of Engineering](https:/pratt.duke.edu/)

&nbsp;
## Data Processing

### **Creating a list of URLs to scrape**

Before scraping the data from the above listed subdomains, a list of URLs of the webpages and subdirectories needs to be created.

To create this list for each subdomain, a recursive function is used to traverse through the subdirectories and subpages of the subdomain and add the URLs to a dictionary. The dictionary is then converted to a list and saved as a JSON file.

The python script can be found in the `scripts` folder and can be run as follows:

**1. Create a new conda environment and activate it:** 
```
conda create --name nlp python=3.8
conda activate nlp
```
**2. Install python package requirements:** 
```
pip install -r requirements.txt 
```
**3. Change directory to the scripts folder:** 
```
cd scripts
```
**4. Run the URL list creation script:** 
```
python get_subpages.py <subdomain_url> <json_file_name>
```

For example, to create the list of URLs for the subdomain [https://ai.meng.duke.edu](https://ai.meng.duke.edu/), the following command can be run:

```bash
python python get_subpages.py "https://ai.meng.duke.edu" "../data/web_scraping/ai_meng_duke_edu.json"
```

### **Scraping text data from the webpages**

Once the list of URLs is created, the text data from all the webpages of a subdomain need to be scraped. As each webpage has a different structure, parsing the HTML of each webpage and extracting the required text data is a tedious and time-consuming task.

Hence, the [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) library is used to parse the HTML of the webpages and extract the text data. The text data is then cleaned using [html2text](https://pypi.org/project/html2text/) package and stored in a .txt file.

The python script to scrape text can be found in the `scripts` folder. Assuming you are in the same conda environment as the previous step, the python script can be run as follows:

**1. Change directory to the scripts folder:** 
```
cd scripts
```
**2. Run the web scraping script:** 
```
python scrape.py <json_file_name> <data_directory>
```

For example, to scrape the text data from the subdomain [https://ai.meng.duke.edu](https://ai.meng.duke.edu/), the following command can be run:

```bash
python scrape.py "../data/web_scraping/ai_meng_duke_edu.json" "../data/web_scraping"
```

### **Data Processing**

Once the text data is scraped from the webpages, it needs to be processed and indexed in Elasticsearch. The following steps are performed to process and index the text data:
- Read the text data from all the .txt files
- Remove whitespaces, angle brackets, html tags and urls
- Webpages of a particular subdomain contain specific headers and footers. These headers and footers are removed from the text data
- Remove any non-unicode characters from the text data
- Chunk the text data into smaller chunks of 250 words each (with a 10 word overlap and respecting sentence boundaries)

Now, to create data for pre-training LLMs, the following steps are performed:
- Create a list of all the chunks of text data
- Write the chunks of text data to a .txt file with each chunk separated by a newline character

To create data for fine-tuning LLMs, the following steps are performed:
- Create a list of all the chunks of text data
- Loop through each chunk of text data and use the OpenAI API to generate pairs of questions and answers for each chunk of data
- The instruction prompt for the OpenAI API is as follows (where `<passage>` is the chunk of text data):
```
I have a short passage given below. Can you please create a list of question answer pairs from the passage which I can use to populate the faq section of my website? Please follow the format: [{\"question\": \"What is the capital of India?\", \"answer\": \"New Delhi\"}, {\"question\": \"Which is the largest state in India?\", \"answer\": \"Rajasthan\"}]\n\nPassage:\n```<passage>```
```
- Write the generated question-answer pairs to a .json file

The python script to process and index the text data can be found in the `scripts` folder. Assuming you are in the same conda environment as the previous step, the python script can be run as follows:

**1. Change directory to the scripts folder:** 
```
cd scripts
```
**2. Run the text preprocessing for pre-training LLMs:** 
```
python process_pretrain_data.py "../data/web_scraping"
```
**3. Run the text preprocessing for fine-tuning LLMs:** 
```
python process_finetune_data.py "../data/web_scraping"
```

&nbsp;
## Pre-training Llama-2-7b-hf

The Duke ChatBot pipeline is a question answering system that allows users to ask questions about the Duke University and get answers to their questions. The pipeline consists of the following components:
- **Document Store:** Elasticsearch document store to store the text scraped from multiple websites and webpages
- **Retriever:** BM25 retriever to retrieve the relevant documents from the document store
- **Answer Generator:** A T5 based model to rephrase the formation of the top document returned by the BM25 Retriever based on the question asked

&nbsp;
## Fine-tuning Llama-2-7b-hf

The Duke ChatBot pipeline is a question answering system that allows users to ask questions about the Duke University and get answers to their questions. The pipeline consists of the following components:
- **Document Store:** Elasticsearch document store to store the text scraped from multiple websites and webpages
- **Retriever:** Dense Passage Retrieval (DPR) model (`facebook/dpr-ctx_encoder-single-nq-base`) to retrieve the relevant documents from the document store
- **Reader:** Reader model (`deepset/roberta-base-squad2`) to extract the answer from the retrieved documents
- **Answer Generator:** A T5 or ChatGPT module to rephrase the formation of the answer returned by the Reader based on the question asked

&nbsp;
## Performance Evaluation and Metrics

Due to the unsupervised nature of the data, there is no ground truth to evaluate the performance of the Duke ChatBot pipeline. However, the performance of the pipeline can be evaluated by asking questions to the pipeline and checking if the answer returned by the pipeline is relevant to the question asked.

### **Manual Qualitative Evaluation**
A list of 50 questions were asked to the Duke ChatBot pipeline and the answers returned by the pipeline were evaluated manually. Each answer was evaluated on a scale of 0 to 3 as follows:
- 0: The answer is not relevant to the question asked
- 1: No answer is returned by the pipeline
- 2: The answer is partially relevant to the question asked
- 3: The answer is relevant to the question asked

Based on the evaluation of different pipelines, the following table shows the performance of the Duke ChatBot pipeline:

| Pipeline | Incorrect Answer | No Answer | Partially Relevant Answer | Fully Relevant Answer |
| --- | :---: | :---: | :---: | :---: |
| Pre-training Llama-2-7b-hf | 76% | 0% | 24% | 0% |
| Fine-tuning Llama-2-7b-hf| 32% | 0% | 50% | 18% |
| RAG with GPT-4 | **0%** | **32%** | **4%** | **64%** |

The detailed question-answer evaluation can be found in the `performance_testing` folder and the analysis can be found in the `test_answers_analysis.xlsx` file.

&nbsp;
## Risks and Limitations

The Duke ChatBot has the following risks and limitations:
- The ChatBot is only able to answer questions about Pratt School of Engineering and its departments, programs, and courses. The pipeline is not able to answer questions about other schools and departments at Duke University.
- The ChatBot is only able to answer questions based on the information scraped from the website as on April 5, 2023. The pipeline is not able to answer questions about the latest updates on the website.
- The ChatBot can provide wrong answers to time sensitive questions if the data on the website was not updated as on April 5, 2023.

&nbsp;
## Project Structure
The project structure is as follows:
```
├── data                                        <- directory for project data (text data scraped from websites)
├── notebooks                                   <- directory to store any exploration notebooks used
├── performance_testing                         <- directory to store performance testing data
    ├── Duke ChatBot_April 23, 2023_18.48.xlsx  <- user survey data
    ├── test_answers_analysis.xlsx              <- analysis of the answers returned by the pipeline
    ├── test_answers.csv                        <- answers returned by the pipeline
    ├── test_questions.csv                      <- questions asked to the pipeline
├── scripts                                     <- directory for pipeline scripts or utility scripts
    ├── chatbot.py                              <- chatbot pipeline server script
    ├── chatgpt_qa.py                           <- chatgpt answer generator script
    ├── get_subpages.py                         <- script to get subpage urls of a website
    ├── helper_functions.py                     <- helper functions used in the pipeline
    ├── index_in_es.py                          <- script to index data in ElasticSearch
    ├── scrape.py                               <- script to scrape data from a website
    ├── t5_qa.py                                <- t5 answer generator script
    ├── testing.py                              <- script to generate answers for manual qualitative evaluation
├── .gitignore                                  <- git ignore file
├── config.json                                 <- config file to store api keys
├── LICENSE                                     <- license file
├── README.md                                   <- description of project and how to set up and run it
├── requirements.txt                            <- requirements file to document dependencies
```

## References

- [Lightning-AI/lit-gpt](https://github.com/Lightning-AI/lit-gpt)
- [Farm-Haystack](https://haystack.deepset.ai)
- [HuggingFace Transformers](https://huggingface.co/transformers/)
- [ChatGPT API](https://platform.openai.com/docs/guides/chat)