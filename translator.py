print('Hello, World!')

LANGUAGE_CHOICES_TEXT = 'Type "en" if you want to translate from French into English, or' \
                        '"fr" if you want to translate from English into French:\n>'

WORD_INPUT_TEXT = 'Type the word you want to translate:\n>'

RESULT_TEXT = 'You chose "{language}" as the language to translate "{word}" to.'

def main():
    language = input(LANGUAGE_CHOICES_TEXT)
    word = input(WORD_INPUT_TEXT)
    print(RESULT_TEXT.format(language=language, word=word))


if __name__ == '__main__':
    main()
