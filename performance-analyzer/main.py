from utils.json import JsonUtil

def main():
    base = 'samples/'
    keyboards = ['gboard', 'swiftkey', 'samsung']
    cases = [
        'normal',
        'normal_2',
        'autocorrect',
        'prediction',
        'typo',
        'change',
        'word_delete',
        'delete_end',
        'insert_middle',
        'typo_middle',
        'change_middle',
        'gesture'
    ]

    for case in cases:
        for keyboard in keyboards:
            sample_data = JsonUtil.get_sample_data(base + keyboard + '/' + case + '.json')
            print(sample_data)


if __name__ == "__main__":
    main()
