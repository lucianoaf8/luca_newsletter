# scripts\db\queries.py

# quotes
quotes='''
SELECT id, quote, source, contextual_notes, author_name, author_overview, 
       author_key_works, timestamp
FROM quotes
WHERE used_in_newsletter = 0;
'''

# authors
authors='''
SELECT id, author, birth_year, death_year, nationality, profession, 
       known_for, timestamp
FROM authors
WHERE used_in_newsletter = 0;
'''

# english tips
english_tips='''
SELECT id, category, title, content, subcontent1, subcontent2, quick_tip, 
       used_in_newsletter, timestamp
FROM english_tips
WHERE used_in_newsletter = 0;
'''

# daily challenges
daily_challenges='''
SELECT id, category, challenge, instructions, motivation, used_in_newsletter, 
       timestamp
FROM daily_challenges
WHERE used_in_newsletter = 0;
'''

