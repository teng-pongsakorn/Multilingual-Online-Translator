import requests
import os
from bs4 import BeautifulSoup
import argparse


QUERY_URL = "https://context.reverso.net/translation/{}-{}/{}"
LANGUAGES = ['arabic', 'german', 'english', 'spanish', 'french', 'hebrew', 'japanese',
             'dutch', 'polish', 'portuguese', 'romanian', 'russian', 'turkish', 'all']
START_CHOICE = 1
HEADERS = {
        "User-Agent": "Mozilla / 5.0(X11;Ubuntu; Linuxx86_64;rv: 83.0) Gecko / 20100101 Firefox / 83.0 "
    }

FAIL_TRANSLATE_MESSAGE = "Sorry, unable to find {}"


def display_language_choices():
    print("Translator supports:")
    for i, lang in enumerate(LANGUAGES, start=START_CHOICE):
        print("{}. {}".format(i, lang))


def extract_translated_words(bs_obj):
    translations = [a.text.strip() for a in bs_obj.find_all('a', class_="translation")][1:]
    return translations


def extract_examples(bs_obj):
    examples = []
    for elem in bs_obj.find_all('div', class_='example'):
        examples.append(":\n".join(x.text.strip() for x in elem.find_all('span', class_='text')))
    return examples


def search(from_language, to_language, word):

    url = QUERY_URL.format(from_language.lower(), to_language.lower(), word)
    response = requests.get(url, headers=HEADERS)
    if response:
        soup = BeautifulSoup(response.content, 'html.parser')
        translations = extract_translated_words(soup)
        examples = extract_examples(soup)
        content = '{} Translations:'.format(to_language.capitalize())
        content += "\n".join(translations)
        content += '\n\n{} Examples:\n'.format(to_language.capitalize())
        content += '\n\n'.join(examples)
        return content


def search_all(from_language, word):
    template = '''\n{} translations:\n{}\n\n{} Example:\n{}\n'''
    other_languages = list(LANGUAGES[:-1]) # not include 'all'
    from_idx = other_languages.index(from_language)
    from_language = other_languages.pop(from_idx)
    content = []
    with requests.Session() as sess:
        for other in other_languages:
            url = QUERY_URL.format(from_language.lower(), other.lower(), word)
            response = sess.get(url, headers=HEADERS)
            if response:
                soup = BeautifulSoup(response.content, 'html.parser')
                translation = extract_translated_words(soup)[0]   # only the first result
                example = extract_examples(soup)[0]
                content.append(template.format(other.lower(), translation, other.lower(), example))

    return "".join(content) if content else None


def save_to_file(name, content, display=True):
    dir = os.getcwd()
    filename = "{}.txt".format(name)
    path = os.path.join(dir, filename)
    with open(path, 'w', encoding='utf-8') as f:
        print(content.strip(), file=f)
        if display:
            print(content)
        return path


def make_check_valid_choice(choices):
    '''function to pass in ArgumentParser.add_argument() for input validation'''
    def check_valid_choice(lang):
        if lang not in choices:
            raise argparse.ArgumentTypeError("Sorry, the program doesn't support {}".format(lang))
        return lang
    return check_valid_choice


class MyArgumentParser(argparse.ArgumentParser):

    def error(self, message):
        '''customize error message when the input language not supported'''
        arg_name, text = message.split(':')
        arg_name = arg_name.split(' ')[1]
        if arg_name.strip() in {'from_language', 'to_language'}:
            print(text.strip())
            self.exit(2, None)
        else:
            super(MyArgumentParser, self).error(message)


def main():
    my_parser = MyArgumentParser() # argparse.ArgumentParser()
    my_parser.add_argument('from_language', choices=LANGUAGES[:-1], type=make_check_valid_choice(LANGUAGES[:-1]))
    my_parser.add_argument('to_language', choices=LANGUAGES, type=make_check_valid_choice(LANGUAGES))
    my_parser.add_argument('word', type=str, help='a word in the original language')
    args = my_parser.parse_args()
    try:
        if args.to_language == 'all':
            content = search_all(args.from_language, args.word)
            if content is not None:
                print("content is None:", content is None)
                save_to_file(args.word, content, display=True)
            else:
                print(FAIL_TRANSLATE_MESSAGE.format(args.word))
        else:
            content = search(args.from_language, args.to_language, args.word)
            if content is not None:
                save_to_file(args.word, content, display=True)
            else:
                print(FAIL_TRANSLATE_MESSAGE.format(args.word))
    except requests.ConnectionError:
        print("Something wrong with your internet connection")



if __name__ == '__main__':
    main()
