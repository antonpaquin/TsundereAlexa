import json

version = '1.0'


def lambda_handler(event, context):
    # Top level handler for the request
    event_type = event['request']['type']
    return {
        'LaunchRequest': on_launch,
        'IntentRequest': handle_intent,
    }.get(event_type, default_event_handler)(event)
    

def plain_speech(speech):
    # Return a simple response that says something via text
    # Generating audio files, sending them to s3 (to be deleted soon after), and returning a URL to those
    # is probably the way to get actually good-sounding results
    return {
        'version': version,
        'response': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': speech,
            },
        },
    }


def on_launch(event):
    # "Alexa, open an anime voice" what do we do here?
    return plain_speech('anta baka')


def handle_intent(event):
    # Handle (custom and otherwise) intents
    intent = event['request']['intent']['name']
    return {
        'VoiceIntent': intent_say_voice,
    }.get(intent)(event)
    
    
def default_event_handler(event):
    # Default handler for when the event type is unexpected
    return plain_speech('Event type ' + event['request']['type'])
    

def intent_say_voice(event):
    # Main intent: we get a request to repeat something in an anime voice
    query = event['request']['intent']['slots']['query']['value']
    return plain_speech(japanify(query))


def default_intent_handler(event):
    # I don't think this happens? No idea what they're sending me
    return plain_speech('anta baka')
    

def japanify(text):
    # Makes a decent approximation of the process of turning english into kana
    # Actually it's not decent, it's pretty bad
    # I'd like to go through IPA as an intermediate representation or something
    consonants = set('bcdfghjklmnpqrstvwxyz')
    kana = {
        'a', 'i', 'u', 'e', 'o',
        'ka', 'ki', 'ku', 'ke', 'ko',
        'sa', 'shi', 'su', 'se', 'so',
        'ta', 'chi', 'tsu', 'te', 'to',
        'na', 'ni', 'nu', 'ne', 'no',
        'ha', 'hi', 'fu', 'he', 'ho',
        'ma', 'mi', 'mu', 'me', 'mo',
        'ya', 'yu', 'yo',
        'ra', 'ri', 'ru', 're', 'ro',
        'wa', 'wo',
        'n',
        'ga', 'gi', 'gu', 'ge', 'go',
        'za', 'ji', 'zu', 'ze', 'zo',
        'da', 'di', 'dsu', 'de', 'do',
        'ba', 'bi', 'bu', 'be', 'bo',
        'pa', 'pi', 'pu', 'pe', 'po',
        'ja', 'ji', 'ju', 'jo',
        'kya', 'kyu', 'kyo',
        'sha', 'shu', 'sho',
        'cha', 'chu', 'cho',
        'nya', 'nyu', 'nyo',
        'hya', 'hyu', 'hyo',
        'mya', 'myu', 'myo',
        'rya', 'ryu', 'ryo',
        'gya', 'gyu', 'gyo',
        'bya', 'byu', 'byo',
        'pya', 'pyu', 'pyo',
    }

    # Do some preprocessing on the text 
    # -- normalize to lowercase,
    text = text.lower()
    # And do a bunch of replacements that I just thought of
    text = text.replace('l', 'r')
    text = text.replace('hu', 'fu')
    text = text.replace('th', 'd')
    text = text.replace('x', 'kusu')
    text = text.replace('v', 'f')
    text = text.replace('tu', 'tsu')
    text = text.replace('q', 'k')
    text = text.replace('wh', 'w')
    text = text.replace('we', 'ue')
    text = text.replace('wi', 'ui')
    text = text.replace('wu', 'u')
    text = text.replace('oo', 'u')
    # 'c' is 'k' unless it's 'ch'
    for idx in range(len(text) - 1):
        if text[idx] == 'c' and text[idx + 1] != 'h':
            text = text[:idx] + 'k' + text[idx + 1:]
    # Undouble consonants
    for char in consonants:
        text = text.replace(char * 2, char)
    
    # Now we go through and hopefully everything is kana or easily converted
    converted = []
    while text:
        # Handle whitespace first
        if text[:1] == ' ':
            converted.append(' ')
            text = text[1:]
            continue
        if text[:1] in kana:
            converted.append(text[:1])
            text = text[1:]
            continue
        if text[:2] in kana:
            converted.append(text[:2])
            text = text[2:]
            continue
        if text[:3] in kana:
            converted.append(text[:3])
            text = text[3:]
            continue
        # Meh, we can ignore 'w'
        if text[:1] == 'w':
            text = text[1:]
            continue
        # 'y' is usually at least somewhat close to 'i' 
        if text[:1] == 'y':
            converted.append('i')
            text = text[1:]
            continue
        # 'toraburu' 'doragon'
        if text[:1] in {'t', 'd'}:
            converted.append(text[:1] + 'o')
            text = text[1:]
            continue
        # For everything else consonant + 'u' is my best guess
        converted.append(text[:1] + 'u')
        text = text[1:]
    
    return ''.join(converted)
