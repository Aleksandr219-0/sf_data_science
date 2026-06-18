import numpy as np


def smart_predict(number: int = 1) -> int:
    """Угадываем число бинарным поиском.

    Args:
        number (int, optional): Загаданное число. Defaults to 1.

    Returns:
        int: Число попыток
    """
    count = 0
    low = 1
    high = 100

    while True:
        count += 1
        predict_number = (low + high) // 2

        if predict_number == number:
            return count
        if predict_number < number:
            low = predict_number + 1
        else:
            high = predict_number - 1
            
def score_game(predict_func) -> int:
    """За какое количество попыток в среднем за 1000 подходов угадывает наш алгоритм.

    Args:
        predict_func: функция угадывания

    Returns:
        int: среднее количество попыток
    """
    count_ls = []
    np.random.seed(1)  # фиксируем сид для воспроизводимости [web:15][web:18]
    random_array = np.random.randint(1, 101, size=1000)  # загадали список чисел

    for number in random_array:
        count_ls.append(predict_func(number))

    score = int(np.mean(count_ls))
    print(f"Ваш алгоритм угадывает число в среднем за: {score} попыток")
    return score

if __name__ == "__main__":
    score_game(smart_predict)
    