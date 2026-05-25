from performance_analyzer.error_rate import ErrorRateCalculator
from performance_analyzer.typing_path import TypingPathCalculator
from performance_analyzer.typing_speed import TypingSpeedCalculator
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

            if len(sample_data) > 0:
                print(base + keyboard + '_' + case + '.json')
                calculate_metrics(sample_data)
                print('')

def calculate_metrics(sequence:list):
    typing_speed_calculator = TypingSpeedCalculator(sequence)
    error_rate_calculator = ErrorRateCalculator(sequence, 'tr')
    typing_path_calculator = TypingPathCalculator(sequence)
    typing_path_calculator.calculate()
    typing_path_calculator.detect_edit_operations()
    revised_text_length = typing_path_calculator.get_revised_text_length()

    print('WPM: ', typing_speed_calculator.wpm(interrupted_time=0))
    print('KSPS:', typing_speed_calculator.ksps(interrupted_time=0))
    print('KSPC:', error_rate_calculator.kspc(additional_characters=revised_text_length))
    print('ER:', error_rate_calculator.error_rate())
    print('Error MSD:', error_rate_calculator.error_msd())
    print('Auto-correction MSD:', typing_path_calculator.auto_correction_msd())
    print('Corrected Error MSD:', typing_path_calculator.corrected_error_msd())
    print('Revised Text Length:', revised_text_length)
    print('Duration:', typing_speed_calculator.get_duration(), 'seconds')
    print('Language:', error_rate_calculator.text_language())
    print('Path:')
    typing_path_calculator.print_path()
    print('Final:\n' + typing_speed_calculator.get_final_text())

if __name__ == "__main__":
    main()
