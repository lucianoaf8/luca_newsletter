# -*- coding: utf-8 -*-

import os
import sys
import json
import requests
import time
from datetime import datetime
from dotenv import load_dotenv
from requests.exceptions import RequestException, HTTPError
import re
from typing import List, Dict, Any

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

from scripts.utils.logger_config import get_logger
from scripts.db.fetch_queries import execute_query
from scripts.utils.db_insert_api_calls import insert_api_response
from scripts.utils.db_connection import get_db_connection, close_connection

# Load environment variables
load_dotenv()

# Initialize logger
logger = get_logger('word_of_the_day')

# API settings
MW_API_KEY = os.getenv('MERRIAM_WEBSTER_KEY')
MW_BASE_URL = 'https://www.dictionaryapi.com/api/v3/references/learners/json'
MW_AUDIO_BASE_URL = 'https://media.merriam-webster.com/audio/prons/en/us/mp3'

query = '''
SELECT id, category, word, sentence, used_in_newsletter, created, updated
FROM word_of_the_day
WHERE meta_id IS NULL;
'''

def save_output(output, word):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'word_of_the_day_{word}_{timestamp}.json'
    file_path = os.path.join(project_root, 'data', 'fetched_results', 'word_of_the_day', filename)

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, 'w') as f:
        json.dump(output, f, indent=4)

    logger.info(f"Output saved to {file_path}")
    return file_path

def fetch_word_definition(word):
    """Fetch word details from Merriam-Webster API"""
    url = f"{MW_BASE_URL}/{word}"
    params = {'key': MW_API_KEY}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Check for HTTP errors
        return response.json()
    except HTTPError as e:
        logger.error(f"HTTP error while fetching definition for {word}: {e}")
    except RequestException as e:
        logger.error(f"Failed to fetch definition for {word}: {e}")
    return None


def parse_short_definitions(shortdef: List[str]) -> List[str]:
    """Parse short definitions, splitting by {bc} and removing extra whitespace."""
    all_definitions = []
    for def_string in shortdef:
        split_defs = re.split(r'\s*\{bc\}\s*', def_string)
        all_definitions.extend([def_.strip() for def_ in split_defs if def_.strip()])
    return all_definitions

def extract_examples(dt: List[Any]) -> List[str]:
    """Extract examples from the definition text (dt) structure."""
    examples = []
    for item in dt:
        if isinstance(item, list) and item[0] == 'vis':
            for vis in item[1]:
                if 't' in vis:
                    # Remove italics tags and trim whitespace
                    example = re.sub(r'\{/?it\}', '', vis['t']).strip()
                    examples.append(example)
    return examples

def extract_grammatical_info(word_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract detailed grammatical information."""
    gram_info = {
        'main_gram': word_data.get('gram'),
        'additional_info': []
    }
    
    # Check for additional grammatical information in the definition structure
    if 'def' in word_data:
        for def_block in word_data['def']:
            if 'sseq' in def_block:
                for sense_seq in def_block['sseq']:
                    for sense in sense_seq:
                        if isinstance(sense, list) and len(sense) > 1:
                            sense_data = sense[1]
                            if 'gram' in sense_data:
                                gram_info['additional_info'].append(sense_data['gram'])
    
    return gram_info

def extract_phrases_idioms(word_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract phrases and idioms related to the word."""
    phrases_idioms = []
    if 'dros' in word_data:
        for dro in word_data['dros']:
            phrase = {
                'phrase': dro.get('drp'),
                'definition': '',
                'examples': []
            }
            if 'def' in dro:
                for def_block in dro['def']:
                    if 'sseq' in def_block:
                        for sense_seq in def_block['sseq']:
                            for sense in sense_seq:
                                if isinstance(sense, list) and len(sense) > 1:
                                    sense_data = sense[1]
                                    if 'dt' in sense_data:
                                        phrase['definition'] += ' '.join([item[1] for item in sense_data['dt'] if isinstance(item, list) and item[0] == 'text'])
                                        phrase['examples'].extend(extract_examples(sense_data['dt']))
            phrases_idioms.append(phrase)
    return phrases_idioms

def update_word_of_the_day(conn, word_id: int, word_data: List[Dict[str, Any]]):
    cursor = conn.cursor()

    try:
        # Disable autocommit
        conn.autocommit = False

        # Extract relevant data from the API response
        if not word_data or not isinstance(word_data[0], dict):
            raise ValueError("Invalid word data structure")

        entry = word_data[0]
        meta = entry.get('meta', {})
        hwi = entry.get('hwi', {})
        
        meta_id = meta.get('id', '')
        meta_uuid = meta.get('uuid', '')
        meta_src = meta.get('src', '')
        meta_section = meta.get('section', '')
        
        target = meta.get('target', {})
        meta_target_tuuid = target.get('tuuid', '')
        meta_target_tsrc = target.get('tsrc', '')
        
        meta_stems = ', '.join(meta.get('stems', []))
        meta_offensive = bool(meta.get('offensive', False))
        
        headword = hwi.get('hw', '')
        part_of_speech = entry.get('fl', '')
        
        pronunciations = hwi.get('prs', [])
        pronunciation_us = ''
        pronunciation_uk = ''
        audio_url_us = ''
        audio_url_uk = ''
        
        for pr in pronunciations:
            if 'ipa' in pr:
                if 'l' not in pr or pr.get('l') != 'British':
                    pronunciation_us = pr['ipa']
                    if 'sound' in pr and 'audio' in pr['sound']:
                        audio_file = pr['sound']['audio']
                        audio_subdir = audio_file[0] if audio_file[0].isalpha() else 'number'
                        audio_url_us = f"{MW_AUDIO_BASE_URL}/{audio_subdir}/{audio_file}.mp3"
                elif pr.get('l') == 'British':
                    pronunciation_uk = pr['ipa']
                    if 'sound' in pr and 'audio' in pr['sound']:
                        audio_file = pr['sound']['audio']
                        audio_subdir = audio_file[0] if audio_file[0].isalpha() else 'number'
                        audio_url_uk = f"{MW_AUDIO_BASE_URL}/{audio_subdir}/{audio_file}.mp3"
        
        grammatical_note = entry.get('gram', '')
        grammatical_info = extract_grammatical_info(entry)
        grammatical_info_str = '; '.join([f"{k}: {v}" for k, v in grammatical_info.items() if v])
        
        # Handle short definitions
        app_shortdef = meta.get('app-shortdef', {})
        shortdef = app_shortdef.get('def', [])
        short_definitions = parse_short_definitions(shortdef)
        shortdef_1 = short_definitions[0] if len(short_definitions) > 0 else None
        shortdef_2 = short_definitions[1] if len(short_definitions) > 1 else None
        shortdef_3 = short_definitions[2] if len(short_definitions) > 2 else None
        short_definitions_str = '; '.join(short_definitions)
        
        # Handle examples
        examples = []
        if 'def' in entry:
            for def_block in entry['def']:
                if isinstance(def_block, dict) and 'sseq' in def_block:
                    for sense_seq in def_block['sseq']:
                        for sense in sense_seq:
                            if isinstance(sense, list) and len(sense) > 1:
                                sense_data = sense[1]
                                if 'dt' in sense_data:
                                    examples.extend(extract_examples(sense_data['dt']))
        example_1 = examples[0] if len(examples) > 0 else None
        example_2 = examples[1] if len(examples) > 1 else None
        examples_str = '; '.join(examples)
        
        # Handle related words
        related_words = []
        if 'uros' in entry:
            for uro in entry['uros']:
                related_word = {
                    'word': uro.get('ure', ''),
                    'part_of_speech': uro.get('fl', ''),
                    'pronunciation': next((pr['ipa'] for pr in uro.get('prs', []) if 'ipa' in pr), ''),
                    'audio_file': '',
                    'grammatical_note': uro.get('gram', '')
                }
                if 'prs' in uro:
                    for pr in uro['prs']:
                        if 'sound' in pr and 'audio' in pr['sound']:
                            related_audio = pr['sound']['audio']
                            related_subdir = related_audio[0] if related_audio[0].isalpha() else 'number'
                            related_word['audio_file'] = f"{MW_AUDIO_BASE_URL}/{related_subdir}/{related_audio}.mp3"
                            break
                related_words.append(related_word)
        related_words_str = '; '.join([f"{rw['word']} ({rw['part_of_speech']})" for rw in related_words])
        
        # Extract phrases and idioms
        phrases_idioms = extract_phrases_idioms(entry)
        phrases_idioms_str = '; '.join([f"{pi['phrase']}: {pi['definition']}" for pi in phrases_idioms])

        # Update the word_of_the_day table
        update_query = """
        UPDATE word_of_the_day
        SET meta_id = %s, meta_uuid = %s, meta_src = %s, 
            meta_section = %s, meta_target_tuuid = %s, 
            meta_target_tsrc = %s, meta_offensive = %s, 
            headword = %s, part_of_speech = %s, 
            pronunciation_us = %s, pronunciation_uk = %s, 
            audio_file_us = %s, audio_file_uk = %s, 
            grammatical_note = %s, grammatical_info = %s,
            shortdef_1 = %s, shortdef_2 = %s, shortdef_3 = %s,
            short_definitions = %s, example_1 = %s, example_2 = %s,
            examples = %s, related_words = %s, phrases_idioms = %s
        WHERE id = %s
        """
        cursor.execute(update_query, (
            meta_id, meta_uuid, meta_src,
            meta_section, meta_target_tuuid,
            meta_target_tsrc, meta_offensive,
            headword, part_of_speech,
            pronunciation_us, pronunciation_uk,
            audio_url_us, audio_url_uk,
            grammatical_note, grammatical_info_str,
            shortdef_1, shortdef_2, shortdef_3,
            short_definitions_str, example_1, example_2,
            examples_str, related_words_str, phrases_idioms_str,
            word_id
        ))
        
        # If we've made it this far, commit the transaction
        conn.commit()
        logger.info(f"Updated word_of_the_day table for word ID: {word_id}")
        return True
    except Exception as e:
        # If any error occurs, roll back the transaction
        conn.rollback()
        logger.error(f"Error processing word ID {word_id}: {str(e)}")
        return False
    finally:
        cursor.close()
        # Re-enable autocommit
        conn.autocommit = True

def main():
    # Fetch all words from the database
    result = execute_query(query)
    
    if not result.empty:
        conn = get_db_connection()
        try:
            for index, row in result.iterrows():
                word_id = int(row['id'])
                word_of_the_day = row['word']
                logger.info(f"Processing word: {word_of_the_day} (ID: {word_id})")
                
                try:
                    # Fetch definition of the word from Merriam-Webster API
                    word_definition = fetch_word_definition(word_of_the_day)
                    
                    if word_definition:
                        logger.info(f"Definition fetched for {word_of_the_day}")
                        
                        output_file_path = save_output(word_definition, word_of_the_day)
                        
                        # Prepare combined_params
                        combined_params = {
                            'word_id': word_id,
                            'word': word_of_the_day,
                            'api_url': f"{MW_BASE_URL}/{word_of_the_day}",
                            'api_key': MW_API_KEY  # Be cautious about logging API keys
                        }
                        
                        # Log the combined API call with the final output
                        script_path = os.path.abspath(__file__)
                        with open(output_file_path, 'r') as f:
                            final_output = json.load(f)
                        
                        insert_api_response(script_path, combined_params, final_output)
                        
                        # Update word_of_the_day table
                        update_success = update_word_of_the_day(conn, word_id, word_definition)
                        
                        if update_success:
                            logger.info(f"API response inserted into database and word_of_the_day updated for word: {word_of_the_day}")
                        else:
                            logger.warning(f"Failed to update word_of_the_day for word: {word_of_the_day}")
                    else:
                        logger.error(f"Failed to fetch definition for {word_of_the_day}")
                
                except Exception as e:
                    logger.error(f"Error processing word {word_of_the_day}: {str(e)}")
                
                # Add a small delay to avoid hitting API rate limits
                time.sleep(1)
        finally:
            close_connection(conn)
    else:
        logger.info("No words fetched from the database")
        
        
if __name__ == "__main__":
    main()