import json
import asyncio
import networkx as nx
from rag_utils import generate, extract_json_data, split_text
from prompt import *

async def generate_domain(llm, doc_splits):
    '''Generate the domain for the documents'''
    # Generate domain
    docs_text = "\n".join([doc.page_content for doc in doc_splits])
    domain = await generate(llm, GENERATE_DOMAIN_PROMPT, {'input_text': docs_text})
    print(f"Domain: {domain}")
    return domain

async def generate_entity_types(llm, doc_splits, domain):
    '''Generate entity types for the documents'''
    # Generate entity types
    doc_text = " ".join([doc.page_content for doc in doc_splits])
    entity_types = await generate(llm, ENTITY_TYPE_GENERATION_JSON_PROMPT, {'task': DEFAULT_TASK.format(domain=domain), 'input_text': doc_text, 'domain': domain}, struct=None, isStructuredResponse=False)
    print(f"Entity types: {entity_types}")
    entity_types = json.loads(entity_types)['entity_types']
    return entity_types

async def generate_entity_types_continuation(llm, doc_splits, domain, entity_types):
    '''Generate entity types continuation for the documents'''
    # Generate entity types continuation
    doc_text = " ".join([doc.page_content for doc in doc_splits])
    entity_types = await generate(llm, ENTITY_TYPE_GENERATION_CONTINUATION_JSON_PROMPT, {'task': DEFAULT_TASK.format(domain=domain), 'input_text': doc_text, 'entity_types': entity_types}, struct=None, isStructuredResponse=False)
    print(f"Entity types continuation: {entity_types}")
    entity_types = json.loads(entity_types)['entity_types']
    return entity_types

async def generate_entities_and_relationships(llm, doc_splits, entity_types):   
    '''Generate entities and relationships for the documents'''
    # Generate entities and relationships in parallel for each document split
    entities_and_relationships = []

    tasks = [generate(llm, ENTITY_RELATIONSHIPS_GENERATION_JSON_PROMPT, {'entity_types': entity_types, 'input_text': doc.page_content}, None, isStructuredResponse=False) for doc in doc_splits]

    for task in asyncio.as_completed(tasks):
        eAndr = await task
        print(eAndr)
        entities_and_relationships.append(eAndr)
        
    return entities_and_relationships
        
def parse_entities_and_relationships(entities_and_relationships):
    '''Parse the entities and relationships'''
    # Parse json data using custom function
    parsed_entities_and_relationships = []
    for eAndr in entities_and_relationships:
        try:
            extracted_data = json.loads(eAndr)
        except:
            print('WARNING: Could not parse JSON data. Attempting to extract manually...')
            extracted_data = extract_json_data(eAndr)
            extracted_data = json.loads(extracted_data)
        print(extracted_data)
        parsed_entities_and_relationships.append(extracted_data)
    return parsed_entities_and_relationships

def create_knowledge_graph(parsed_entities_and_relationships):
    '''Create a knowledge graph from the parsed entities and relationships'''
    graph = nx.Graph()

    for eAndr in parsed_entities_and_relationships:

        for entity in eAndr['entities']:
            graph.add_node(entity['name'], type=entity.get('type'), description=entity.get('description'))

        for relationship in eAndr['relationships']:
            
            if relationship.get('target') != None:
            
                graph.add_edge(relationship['source'], relationship.get('target'), relationship=relationship.get('relationship'), strength=relationship.get('relationship_strength'))
                
    return graph

async def generate_summary(llm, graph):
    '''Generate a summary from the knowledge graph'''
    print(f'Graph: {str(graph)}')
    # Relationships
    relationships = [(edge[0], edge[1], graph.get_edge_data(edge[0], edge[1])) for edge in graph.edges]

    # Generate summary
    entitiesAndRelations = []
    for edge in relationships:
        entitiesAndRelations.append((f"Source: {edge[0]}", f"Description: {graph.nodes[edge[0]].get('description')}"))
        entitiesAndRelations.append((f"Taregt: {edge[1]}", f"Description: {graph.nodes[edge[1]].get('description')}"))
        entitiesAndRelations.append((f"Relationship: {edge[2]['relationship']} \n\n"))
         
    summary = await generate(llm, SUMMARIZE_PROMPT, {'entity_relationships_list': entitiesAndRelations})
    return summary

async def execute_rag_summarization(llm, video_text):
    '''Execute the RAG summarization process for the video text'''
    # Split the text into documents
    doc_splits = split_text(video_text)
    doc_splits = doc_splits[:20]    
    # Generate domain
    domain = await generate_domain(llm, doc_splits)
    
    # Generate entity types
    entity_types = await generate_entity_types(llm, doc_splits, domain)
    
    # Generate entity types continuation
    continuation_count = 7
    for i in range(continuation_count):
        entity_types += await generate_entity_types_continuation(llm, doc_splits, domain, entity_types)
    
    # Generate entities and relationships
    entities_and_relationships = await generate_entities_and_relationships(llm, doc_splits, entity_types)
    
    # Parse entities and relationships
    parsed_entities_and_relationships = parse_entities_and_relationships(entities_and_relationships)
    
    # Create knowledge graph
    graph = create_knowledge_graph(parsed_entities_and_relationships)
    
    # Generate summary
    summary = await generate_summary(llm, graph)
    
    return summary, graph

async def get_relevant_entities(llm, graph, query):
    '''Get relevant entities based on the query'''
    # Generate relevant entities and relationships based on a query
    entity_list = list(graph.nodes(data=True))
    relationship_count = {entity: len(list(graph.neighbors(entity))) for entity, _ in entity_list}
    relevant_entities = await generate(llm, QUERY_ENTITIES_PROMPT, {'query': query, 'entity_list': entity_list, 'relationship_count': relationship_count})
    relevant_entities = json.loads(relevant_entities)
    print(relevant_entities)
    return relevant_entities

async def model_chat(llm, graph, query):
    '''Chat with the model based on the query and the knowledge graph'''
    # Get relevant entities
    relevant_entities = await get_relevant_entities(llm, graph, query)
    
    # Generate response to the query
    relevant_entities_list = [entity for entity in relevant_entities['relevant_entities']]

    relevant_relationships_list = []
    for entity in relevant_entities_list:
        if entity not in graph.nodes:
            continue
        neighbors = list(graph.neighbors(entity))
        for neighbor in neighbors:
            relevant_relationships_list.append((entity, neighbor, graph.get_edge_data(entity, neighbor)))

    relevant_entities_list = [(entity, graph.nodes[entity].get('description')) for entity in relevant_entities_list if entity in graph.nodes]

    response = await generate(llm, QUERY_PROMPT, {'query': query, 'entity_list': relevant_entities_list, 'relationship_list': relevant_relationships_list})
    print(response)
    return response