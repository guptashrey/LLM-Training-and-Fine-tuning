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

The python script to process the text data can be found in the `scripts` folder. Assuming you are in the same conda environment as the previous step, the python script can be run as follows:

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
## Pre-training Llama-2-7b

Llama 2 is a large language model, originally trained on billions of webpages and documents. As part of this project, the model is pre-trained on Duke University data while keeping the original Llama 2 architecture and hyperparameters intact. The hyperparameters used are as follows:
- **Model:** Llama-2-7b
- **Batch Size:** 125
- **Learning Rate:** 6e-4
- **Weight Decay:** 1e-1
- **Beta1:** 0.9
- **Beta2:** 0.95
- **Gradient Clip:** 1.0
- **Warmup Iters:** 2000
- **Max Iters:** 600000 (num_epochs * (epoch_size // micro_batch_size) // devices)

The data is first prepared by tokenizing the text data and converting it into a torch dataset. The model is then trained on the data using the [Lightning](https://www.pytorchlightning.ai/) framework.

The model is trained on a 8 GPUs for 5 epochs. The data preparation and training scripts can be found in the `scripts` and `pretrain` folders respectively. Assuming you are in the same conda environment as the previous step, the python script can be run as follows:

**1. Prepare data for pre-training:** 
```
python scripts/prepare_pretrain.py
```
**2. Run the pre-training script:** 
```
python pretrain/run_pretrain.py
```

&nbsp;
## Fine-tuning Llama-2-7b

The base Llama-2-7b model is fine-tuned on the Duke University data to perform Question Answering (QA) tasks. Fine-tuning is performed using 2 approaches:

### **Approach 1: Fine-tuning all the model weights**

In this approach, all the model weights are fine-tuned on QA data from Duke University. The hyperparameters used are as follows:
- **Model:** Llama-2-7b
- **Batch Size:** 1
- **Learning Rate:** 3e-3
- **Weight Decay:** 0.02
- **Epoch Size:** 1500
- **Num Epochs:** 5
- **Warmup Steps:** 2 * (epoch_size // micro_batch_size) // devices // gradient_accumulation_iters

The data is first prepared by tokenizing the text data and converting it into a torch dataset. The model is then fine-tuned on the data using the [Lightning](https://www.pytorchlightning.ai/) framework.

The model is fine-tuned on a 1 GPUs for 5 epochs. The data preparation and fine-tuning scripts can be found in the `scripts` and `finetune` folders respectively. Assuming you are in the same conda environment as the previous step, the python script can be run as follows:

**1. Prepare data for fine-tuning:** 
```
python scripts/prepare_finetune.py
```
**2. Run the fine-tuning script:** 
```
python finetune/full.py
```

### **Approach 2: Fine-tuning limited set of weights using Adapter Parameter Efficient Fine-Tuning (PEFT)**

In this approach, only a limited set of weights are fine-tuned on QA data from Duke University. The hyperparameters used are as follows:
- **Model:** Llama-2-7b
- **Batch Size:** 1
- **Learning Rate:** 3e-3
- **Weight Decay:** 0.02
- **Epoch Size:** 1500
- **Num Epochs:** 5
- **Warmup Steps:** 2 * (epoch_size // micro_batch_size) // devices // gradient_accumulation_iters

The data is first prepared by tokenizing the text data and converting it into a torch dataset. The model is then fine-tuned on the data using the [Lightning](https://www.pytorchlightning.ai/) framework.

The model is fine-tuned on a 1 GPUs for 5 epochs. The data preparation and fine-tuning scripts can be found in the `scripts` and `finetune` folders respectively. Assuming you are in the same conda environment as the previous step, the python script can be run as follows:

**1. Prepare data for fine-tuning:** 
```
python scripts/prepare_finetune.py
```
**2. Run the fine-tuning script:** 
```
python finetune/adapter_v2.py
```

&nbsp;
## Performance Evaluation and Metrics

Due to the unsupervised nature of the data, there is no ground truth to evaluate the performance of the pre-trained and fine-tuned LLMs. However, the performance of the pipeline can be evaluated by asking questions to the pipeline and checking if the answer returned by the pipeline is relevant to the question asked.

### **Manual Qualitative Evaluation**
A list of 50 questions were asked to the pre-trained/fine-tuned LLMs and the answers returned by the pipeline were evaluated manually. Each answer was evaluated on a scale of 0 to 3 as follows:
- 0: The answer is not relevant to the question asked
- 1: No answer is returned by the pipeline
- 2: The answer is partially relevant to the question asked
- 3: The answer is relevant to the question asked

Based on the evaluation, the following table shows the performance of the different models:

| Pipeline | Incorrect Answer | No Answer | Partially Relevant Answer | Fully Relevant Answer |
| --- | :---: | :---: | :---: | :---: |
| Pre-training Llama-2-7b-hf | 0% | 100% | 0% | 0% |
| Fine-tuning Llama-2-7b-hf| 22% | 0% | 40% | 38% |
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
├── finetune                                    <- directory for fine-tuning scripts
    ├── adapter_v2.py                           <- script to fine-tune LLMs using Adapter PEFT
    ├── full.py                                 <- script to fine-tune LLMs using all the model weights
├── generate                                    <- directory for inference scripts
├── lit_gpt                                     <- directory for LIT-GPT code
├── logs                                        <- directory to store training logs
├── notebooks                                   <- directory to store any exploration notebooks used
├── performance_testing                         <- directory to store performance testing data
    ├── test_answers_analysis.xlsx              <- analysis of the answers returned by the pipeline
├── scripts                                     <- directory for pipeline scripts or utility scripts
    ├── convert_hf_checkpoint.py                <- script to convert a HuggingFace checkpoint to a LIT-GPT checkpoint
    ├── download.py                             <- script to download the pre-trained LLMs from HuggingFace
    ├── get_subpages.py                         <- script to get subpage urls of a website
    ├── prepare_finetune.py                     <- script to tokenize the processed data and create torch datasets
    ├── prepare_pretrain.py                     <- script to tokenize the processed data and create torch datasets
    ├── process_finetune_data.py                <- script to process the scraped data for fine-tuning
    ├── process_pretrain_data.py                <- script to process the scraped data for pre-training
    ├── scrape.py                               <- script to scrape data from the list of subpages
├── .gitattributes                              <- git attributes file
├── .gitignore                                  <- git ignore file
├── config.json                                 <- config file to store api keys
├── LICENSE                                     <- license file
├── README.md                                   <- description of project and how to set up and run it
├── requirements.txt                            <- requirements file to document dependencies
```

## References

- [Lightning-AI/lit-gpt](https://github.com/Lightning-AI/lit-gpt/tree/cf5542a166d71c0026b35428113092eb41029a8f)
- [Farm-Haystack](https://haystack.deepset.ai)
- [HuggingFace Transformers](https://huggingface.co/transformers/)
- [ChatGPT API](https://platform.openai.com/docs/guides/chat)