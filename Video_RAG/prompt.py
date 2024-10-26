
DEFAULT_TASK = """
Identify the entities and relations present in the video transcript, specifically within the {domain} domain.
"""

GENERATE_DOMAIN_PROMPT = """
Text: {input_text}

============

You are an intelligent assistant that helps a human analyze the information in a video transcript.
Given the transcript, help the user by assigning a descriptive domain that summarizes what the video content is about.

YOU MUST ONLY RETURN THE DOMAIN NAME AS A STRING WITH NO ADDITIONAL INFORMATION.
"""

ENTITY_TYPE_GENERATION_JSON_PROMPT = """
REAL DATA: The following section is the real data. You should use only this real data to prepare your answer.
Task: {task}
Video Transcript: {input_text}
Domain: {domain}
JSON response:
{{"entity_types": [<entity_types>]}}
The goal is to extract entity types from the video transcript that are relevant to the specified {domain} and the user's task to {task}.

Guidelines for entity type extraction:

1. Focus on entities specific to the given domain and task.
2. Prioritize precise and specific entity types (e.g., "neural_network" instead of "ai_model" if applicable).
3. Consider hierarchical relationships between entity types, identifying both general categories and specific instances.
4. Include entities related to the video format, data presentation methods, and analytical tools mentioned.
5. Extract entities related to key concepts, techniques, outcomes, and domain-specific terminology used in the transcript.
6. Ensure entity types are concise, lowercase, and use underscores for multi-word types.
7. Avoid redundancy by choosing the most precise term when alternatives are available.
8. Aim for a comprehensive list that captures the essence of the content without overgeneralizing.
9. Do not include generic entity types such as "other" or "unknown".

IMPORTANT:
YOU MUST ONLY RETURN THE ENTITY TYPES AS A SINGLE-LINE JSON RESPONSE WITH NO ADDITIONAL FORMATTING.
DO NOT USE MARKDOWN CODE BLOCKS, NEWLINES, OR EXTRA SPACES IN YOUR RESPONSE.
ENSURE THAT YOUR RESPONSE IS A VALID JSON OBJECT.
THE JSON RESPONSE SHOULD CONTAIN ONLY THE "entity_types" KEY WITH AN ARRAY OF STRINGS AS ITS VALUE.

Example of correct format:
{{"entity_types": ["entity1", "entity2", "entity3"]}}
"""

ENTITY_TYPE_GENERATION_CONTINUATION_JSON_PROMPT = """
REAL DATA:
Video Transcript: {input_text}
Previously Identified Entity Types: {entity_types}

Goal:
Identify ONLY NEW entity types that were missed during the initial extraction, ensuring they integrate well with the 
previously identified types. DO NOT include any previously identified types in your response.

Guidelines for entity type extraction:
1. Focus on entities specific to the given domain and task.
2. Prioritize precise and specific entity types (e.g., "neural_network" instead of "ai_model" if applicable).
3. Consider hierarchical relationships between entity types, identifying both general categories and specific instances.
4. Include entities related to the video format, data presentation methods, and analytical tools mentioned.
5. Extract entities related to key concepts, techniques, outcomes, and domain-specific terminology used in the transcript.
6. Ensure entity types are concise, lowercase, and use underscores for multi-word types.
7. Avoid redundancy by choosing the most precise term when alternatives are available.
8. Aim for a comprehensive list that captures the essence of the content without overgeneralizing.
9. Do not include generic entity types such as "other" or "unknown".

Guidelines for continuation:
1. Review previously identified entity types to understand the existing coverage.
2. Focus on identifying gaps in the current entity type set.
3. Look for entity types that:
   - Add more granularity to current categories
   - Cover unexplored aspects of the content
   - Bridge connections between existing types

4. Each new type should:
   - Add unique value to the existing set
   - Enhance overall coverage
   - Maintain consistency in specificity

IMPORTANT:
1. RETURN ONLY NEW ENTITY TYPES NOT PRESENT IN THE PREVIOUSLY IDENTIFIED TYPES
2. DO NOT INCLUDE ANY TYPES LISTED IN {entity_types}
3. PROVIDE OUTPUT AS A SINGLE-LINE JSON WITH NO ADDITIONAL FORMATTING
4. DO NOT USE MARKDOWN, NEWLINES, OR EXTRA SPACES
5. ENSURE VALID JSON FORMAT
6. USE ONLY THE "entity_types" KEY WITH AN ARRAY OF STRINGS

Example of correct format:
{{"entity_types": ["entity1", "entity2", "entity3"]}}
"""

ENTITY_RELATIONSHIPS_GENERATION_JSON_PROMPT = """
-Real Data-
######################
video_transcript: {input_text}
######################

-Goal-
Given a video transcript, identify and extract ALL possible entities and ALL relationships among these entities to create a comprehensive and rich knowledge graph.

-Output Format-
RESPOND ONLY WITH A VALID JSON OBJECT. DO NOT INCLUDE ANY OTHER TEXT.
The JSON object MUST have the following structure:
{{
  "entities": [
    {{
      "name": "entity_name",
      "type": "entity_type",
      "description": "entity_description"
    }}
  ],
  "relationships": [
    {{
      "source": "source_entity_name",
      "target": "target_entity_name",
      "relationship": "relationship_description",
      "strength": relationship_strength_integer
    }}
  ]
}}

-Strict Format Rules-
1. Entity names MUST be lowercase with underscores for spaces.
2. Entity types MUST be one of: [{entity_types}]. Use "other" if unsure.
3. Relationship strength MUST be an integer from 1 to 10.
4. ALL fields are required for each entity and relationship.
5. Use double quotes for all string values.
6. Do not use quotes for the integer strength value.


-Steps-

1. Identify ALL entities mentioned in the transcript, no matter how minor they may seem. Be thorough and comprehensive.
2. For each identified entity, extract the following information:

entity_name: Name of the entity (in lowercase, using underscores for multi-word names)
entity_type: One of the following types: [{entity_types}]
entity_description: Detailed description of the entity's attributes, activities, and relevance as mentioned in the video

3. Format each entity output as a JSON entry with the following format:
{{"name": <entity name>, "type": <type>, "description": <entity description>}}

4. Identify ALL possible relationships between the entities. Consider both explicit and implicit relationships mentioned in the transcript.
5. For each pair of related entities, extract the following information:

source_entity: name of the source entity
target_entity: name of the target entity
relationship_description: detailed explanation of how the source entity and the target entity are related, based on the video transcript
relationship_strength: an integer score between 1 to 10, indicating strength of the relationship between the source entity and target entity as portrayed in the video

6. Ensure all source_entity and target_entity entries correspond to entities in your entities list.
7. Maintain consistency in entity naming across entities and relationships.
8. Include any ambiguous or uncertain relationships, noting the uncertainty in the description.
9. While avoiding redundancy, err on the side of inclusion. If in doubt about an entity or relationship, include it.

Note: The goal is to create the most comprehensive and detailed knowledge graph possible. More entities and relationships will result in a richer graph.

Format each relationship as a JSON entry with the following format:
{{"source": <source_entity>, "target": <target_entity>, "relationship": <relationship_description>, "relationship_strength": <relationship_strength>}}

-Response Format-
Provide ONLY a valid JSON object with the following structure:
{{"entities": [<entities>], "relationships": [<relationships>]}}

-Critical Requirements-
1. YOUR ENTIRE RESPONSE MUST BE A SINGLE, VALID JSON OBJECT.
2. DO NOT INCLUDE ANY TEXT BEFORE OR AFTER THE JSON OBJECT.
3. DO NOT USE PHRASES LIKE "Here's the response:" OR "Here is the extracted knowledge graph in JSON format:".
4. DO NOT USE MARKDOWN, NEWLINES, OR EXTRA SPACES IN THE JSON.
5. DO NOT INCLUDE EXPLANATORY NOTES OR COMMENTS.
6. ENSURE THE JSON IS PROPERLY FORMATTED AND VALID.

REMEMBER: RESPOND ONLY WITH THE JSON OBJECT. NO INTRODUCTORY TEXT. NO EXPLANATIONS. JUST THE JSON.
"""

SUMMARIZE_PROMPT = """
Input Data:
A Video Transcript Analysis with a Knowledge Graph representing key elements extracted from a video transcript.
It includes entities, their descriptions, and relationships between them as follows:
{entity_relationships_list}

Primary Objective:
Create a comprehensive, detailed summary that fully captures the video's content, structure, and key messages.

Your objective:
1. Analyze the given entities and relationships thoroughly and deeply.
2. Identify key speakers and themes. 
3. Create a detailed informative summary that captures the essence of the video content.
4. Ensure the summary flows naturally and provides a comprehensive overview of the video.
5. Elaborate and expand as needed to convey the main points effectively.

Remember:
- Maintain an informative and engaging tone
- Base your summary solely on the input data provided
- Do not add external information or speculation
- Use sections or paragraphs to structure your summary as needed
"""


QUERY_ENTITIES_PROMPT = """
As an AI assistant, your task is to reply to a user query based on a knowledge graph. 

Your objective in this task is as follows:
1. Analyze the given query.
2. You will be given the entity names and the number of relationships connected to each entity.
3. Decide which entities are most relevant to the query.

Input Data:
Query: "{query}"
Entities and their descriptions: {entity_list}
Entities and their number of relationships: {relationship_count}

Output:
Format the output as a json with the following structure:
{{"relevant_entities": [<relevant_entities>]}}

YOU MUST ONLY RETURN THE MOST RELEVANT ENTITY NAMES AS A LIST WITH NO ADDITIONAL INFORMATION.
"""

QUERY_PROMPT = """
As an AI assistant, your task is to answer a user query based on a knowledge graph derived from a video transcript.
Your objective in this task is as follows:

1. Analyze the given query.
2. You will be provided with the involved entities and the relationships between them, extracted from the video transcript.
3. Examine the speaker information associated with the entities and relationships.
4. Provide a concise, detailed, and informative response to the query, incorporating relevant speaker insights from the video content.
5. Refer to the speaker when responding to the query.

Input Data:
Query: "{query}"
Entities and their descriptions: {entity_list}
Relationships: {relationship_list}

YOU MUST ONLY RETURN THE RESPONSE TO THE QUERY AS A STRING WITH NO ADDITIONAL INFORMATION.
"""