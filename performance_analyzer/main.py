from utils.json import JsonUtil
from typing_speed import TypingSpeedCalculator

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

            if len(sample_data) > 0:
                print(base + keyboard + '_' + case + '.json')
                calculate_metrics(sample_data)
                print('')

def calculate_metrics(sequence:list):
    typing_speed_calculator = TypingSpeedCalculator(sequence)

    print('WPM: ', typing_speed_calculator.wpm(interrupted_time=0))


if __name__ == "__main__":
    main()
