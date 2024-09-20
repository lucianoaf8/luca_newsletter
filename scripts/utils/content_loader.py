import json

def load_content(json_path):
    with open(json_path, 'r', encoding='utf-8') as file:
        content = json.load(file)
    return content

def render_template(template_path, content):
    with open(template_path, 'r', encoding='utf-8') as file:
        template = file.read()

    # Header Section
    template = template.replace('{{ header.newsletter_title }}', content.get('header', {}).get('newsletter_title', ''))
    template = template.replace('{{ header.newsletter_username }}', content.get('header', {}).get('newsletter_username', ''))
    template = template.replace('{{ header.newsletter_date }}', content.get('header', {}).get('newsletter_date', ''))
    template = template.replace('{{ header.welcome_message }}', content.get('header', {}).get('welcome_message', ''))
    template = template.replace('{{ presented_by }}', content.get('header', {}).get('presented_by', ''))

    # Weather Section
    weather = content.get('weather', {})
    template = template.replace('{{ weather.icon_file_url }}', weather.get('icon_file_url', ''))
    template = template.replace('{{ weather.temperature }}', str(weather.get('temperature', '')))
    template = template.replace('{{ weather.feels_like_name }}', weather.get('feels_like_name', ''))
    template = template.replace('{{ weather.temperatureApparent }}', str(weather.get('temperatureApparent', '')))
    template = template.replace('{{ weather.description }}', weather.get('description', ''))
    template = template.replace('{{ weather.sunrise_name }}', weather.get('sunrise_name', ''))
    template = template.replace('{{ weather.sunrise }}', weather.get('sunrise', ''))
    template = template.replace('{{ weather.sunset_name }}', weather.get('sunset_name', ''))
    template = template.replace('{{ weather.sunset }}', weather.get('sunset', ''))
    template = template.replace('{{ weather.cloud_cover_name }}', weather.get('cloud_cover_name', ''))
    template = template.replace('{{ weather.cloudCover }}', str(weather.get('cloudCover', '')))
    template = template.replace('{{ weather.precipitation_name }}', weather.get('precipitation_name', ''))
    template = template.replace('{{ weather.precipitationProbability }}', str(weather.get('precipitationProbability', '')))
    template = template.replace('{{ weather.humidity_name }}', weather.get('humidity_name', ''))
    template = template.replace('{{ weather.humidity }}', str(weather.get('humidity', '')))
    template = template.replace('{{ weather.wind_name }}', weather.get('wind_name', ''))
    template = template.replace('{{ weather.windSpeed }}', str(weather.get('windSpeed', '')))
    template = template.replace('{{ weather.uv_index_name }}', weather.get('uv_index_name', ''))
    template = template.replace('{{ weather.uvIndex }}', str(weather.get('uvIndex', '')))

    # Exchange Rates Section
    exchange = content.get('exchange_rates', {})
    template = template.replace('{{ exchange_rates.header }}', exchange.get('header', ''))
    template = template.replace('{{ exchange_rates.cad_brl }}', exchange.get('cad_brl', ''))
    template = template.replace('{{ exchange_rates.cad_brl_change }}', exchange.get('cad_brl_change', ''))
    template = template.replace('{{ exchange_rates.usd_brl }}', exchange.get('usd_brl', ''))
    template = template.replace('{{ exchange_rates.usd_brl_change }}', exchange.get('usd_brl_change', ''))
    template = template.replace('{{ exchange_rates.usd_cad }}', exchange.get('usd_cad', ''))
    template = template.replace('{{ exchange_rates.usd_cad_change }}', exchange.get('usd_cad_change', ''))

    # Quote of the Day
    quote = content.get('quote_of_the_day', {})
    template = template.replace('{{ quote_of_the_day.quote }}', quote.get('quote', ''))
    template = template.replace('{{ quote_of_the_day.source }}', quote.get('source', ''))
    template = template.replace('{{ quote_of_the_day.author_pic }}', quote.get('author_pic', ''))
    template = template.replace('{{ quote_of_the_day.author_name }}', quote.get('author_name', ''))
    template = template.replace('{{ quote_of_the_day.birth_year }}', str(quote.get('birth_year', '')))
    template = template.replace('{{ quote_of_the_day.death_year }}', str(quote.get('death_year', '')))

    # Fun Fact Section
    fun_fact = content.get('fun_fact', {})
    template = template.replace('{{ fun_fact.fun_fact }}', fun_fact.get('fun_fact', ''))

    # Word of the Day
    word = content.get('word_of_the_day', {})
    template = template.replace('{{ word_of_the_day.word }}', word.get('word', ''))
    template = template.replace('{{ word_of_the_day.pronunciation_us }}', word.get('pronunciation_us', ''))
    template = template.replace('{{ word_of_the_day.short_definitions }}', word.get('short_definitions', ''))
    template = template.replace('{{ word_of_the_day.examples }}', word.get('examples', ''))

    # English Tip
    english_tip = content.get('english_tip', {})
    template = template.replace('{{ english_tip.content }}', english_tip.get('content', ''))

    # Historical Event
    historical = content.get('historical_event', {})
    template = template.replace('{{ historical_event.year }}', str(historical.get('year', '')))
    template = template.replace('{{ historical_event.event_description }}', historical.get('event_description', ''))

    # Challenge
    challenge = content.get('challenge', {})
    template = template.replace('{{ challenge.header }}', challenge.get('header', ''))
    template = template.replace('{{ challenge.challenge }}', challenge.get('challenge', ''))
    template = template.replace('{{ challenge.instructions }}', challenge.get('instructions', ''))
    template = template.replace('{{ challenge.motivation }}', challenge.get('motivation', ''))

    # Footer
    footer = content.get('footer', {})
    template = template.replace('{{ footer.goodbye }}', footer.get('goodbye', ''))
    template = template.replace('{{ footer.reply }}', footer.get('reply', ''))
    template = template.replace('{{ footer.unsubscribe }}', footer.get('unsubscribe', ''))

    return template
