import json
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

def split_text(video_text):
    '''split text into chunks'''
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=400, chunk_overlap=0)

    #get docs
    docs = text_splitter.create_documents([video_text])

    #split documents
    doc_splits = text_splitter.split_documents(docs)
    
    return doc_splits

async def generate(llm, prompt, prompt_vals, struct=None, isStructuredResponse=False):
    '''generate a response from a prompt using langchain'''
    input_vars = [key for key in prompt_vals.keys()]
    prompt = PromptTemplate(template=prompt, input_variables=input_vars)

    # Chain
    if isStructuredResponse:
        structured_llm = llm.with_structured_output(struct, method='json_schema')
        chain = prompt | structured_llm 
    else:
        chain = prompt | llm | StrOutputParser()
    
    # Run
    generation = await chain.ainvoke(prompt_vals)
    
    return generation


def extract_json_data(text):
    '''Parse JSON data with entities and relationships structure'''
    def clean_value(value):
        '''Clean and type-convert values as needed'''
        value = value.strip().strip(',').strip('"')
        # Try to convert to integer if it's a number
        try:
            if value.isdigit():
                return int(value)
            return value
        except:
            return value

    def parse_section(section_text):
        '''Parse individual JSON objects from a section'''
        parsed_items = []
        # Find all objects between curly braces
        items = re.findall(r'\{(.*?)\}', section_text, re.DOTALL)
        
        for item in items:
            item_dict = {}
            # Split by lines and process each key-value pair
            lines = [line.strip() for line in item.split('\n') if ':' in line]
            
            for line in lines:
                # Split at first occurrence of : to handle potential colons in values
                key, value = line.split(':', 1)
                key = key.strip().strip('"')
                value = clean_value(value)
                item_dict[key] = value
                
            if item_dict:  # Only add if we parsed some data
                parsed_items.append(item_dict)
                
        return parsed_items

    try:
        # Extract entities section
        entities_match = re.search(r'"entities":\s*\[(.*?)\]', text, re.DOTALL)
        entities = []
        if entities_match:
            entities = parse_section(entities_match.group(1))

        # Extract relationships section
        relationships_match = re.search(r'"relationships":\s*\[(.*?)\]', text, re.DOTALL)
        relationships = []
        if relationships_match:
            relationships = parse_section(relationships_match.group(1))

        # Construct final result
        result = {
            "entities": entities,
            "relationships": relationships
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        print(f"Error parsing JSON data: {str(e)}")
        return json.dumps({"entities": [], "relationships": []})