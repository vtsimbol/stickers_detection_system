import os
import pandas as pd
import numpy as np
import config
import sensors
import visualisation


def load_dataset(file_path):
    return pd.read_csv(file_path, sep=';')


def get_sensor_series_from_dataframe(df, index, offset, sensor_number):
    """
    Получение данных их датафрейма - сырые данные
    :param df: pandas dataframe
    :param index: стартовый индекс в датасете
    :param offset: количество временных отсчетов
    :param sensor_number: номер датчика
    :return: numpy вектор данных за запрошенный интервал
    """
    return df[f'ValueFO{sensor_number:03}'][index : index + offset]


def get_average_temperature_series(df, index, offset, rows=14):
    """
    Получение временного ряда средней температуры по уровням (датчики с 1-32, с 33-64 и т.д.)
    :param df: pandas dataframe
    :param index: стартовый индекс в датасете
    :param offset: количество временных отсчетов
    :param rows: количество уровней датчиков, начиная сверху
    :return: numpy массив средних температур по каждому уровню датчиков
    """
    rows = min(rows, sensors.rows)
    data = np.zeros((rows, offset))
    counter = np.zeros(rows)
    for i in range(0, offset):
        indx = i + index
        for r in range(rows):
            counter[r] = 0
            for c in range(sensors.columns):
                sensor_number = r * sensors.columns + c + 1
                val = f'ValueFO{sensor_number:03}'
                stat = f'StatusFO{sensor_number:03}'
                if 0 <= df[val][indx] <= 300 and df[stat][indx] == 1:
                    data[r][i] += df[val][indx]
                    counter[r] += 1
            if counter[r] != 0:
                data[r][i] = data[r][i] / counter[r]
            else:
                data[r][i] = 0
    return data


def get_difference_between_average_and_sensor_temperature(df, data, index, offset, sensor_number):
    """
    Получение временного ряда разницы между средней температурой на уровне рассматриваемого датчика и его температуры
    :param df: pandas dataframe
    :param data: numpy матрица, полученная из функции get_average_temperature_series
    :param index: стартовый индекс в датасете
    :param offset: количество временных отсчетов
    :param sensor_number: номер рассматриваемого датчика
    :return: numpy вектор для рассматриваемого датчика
    """
    row = int(sensor_number / sensors.columns)
    if row > data.shape[0]:
        raise ValueError('Row number is larger than size of the data array')
    result = np.zeros(offset)
    val = f'ValueFO{sensor_number:03}'
    stat = f'StatusFO{sensor_number:03}'
    for i in range(offset):
        indx = i + index
        if 0 <= df[val][indx] <= 300 and df[stat][indx] == 1:
            result[i] = df[val][indx] - data[row][i]
    return result


def get_derivative(df, index, offset, sensor_number, t=10):
    """
    Получение первой производной конкретного датчика на конкретном интервале
    :param df: pandas dataframe
    :param index: стартовый индекс в датасете
    :param offset: количество временных отсчетов
    :param sensor_number: номер рассматриваемого датчика
    :param t: количество временных отсчетов при вычислении
    :return: numpy вектор первой производной
    """
    result = np.zeros(int(offset / t))
    val = f'ValueFO{sensor_number:03}'
    stat = f'StatusFO{sensor_number:03}'
    for i in range(1, result.shape[0]):
        indx = i * t + index
        indx2 = indx - t
        if 0 <= df[val][indx] <= 300 and df[stat][indx] == 1 and 0 <= df[val][indx2] <= 300 and df[stat][indx2] == 1:
            result[i] = df[val][indx] - df[val][indx2]
    return result


if __name__ == "__main__":
    # Имя файла
    file_name = 'SMS_DC_DataFile_017.csv'
    # Задание анализируемого интервала
    start_index = 7300
    offset = 300
    # Количество уровней датчиков, считая сверху
    rows = 5
    # Перебираемые столбцы датчиков
    columns = [7, 8, 9]
    # Интервал вычисления производной
    T=10

    # load .csv dataset
    df = load_dataset(os.path.join(config.dataset_dir, file_name))
    # get average temp
    data = get_average_temperature_series(df, start_index, offset, rows)
    for column in range(1, sensors.columns + 1):
        # analysis sensors
        sensor_numbers = sensors.sensors[column][:rows]
        labels = []
        series = []
        labels_der = []
        series_der = []
        for i in range(rows):
            der = get_derivative(df, start_index, offset, sensor_numbers[i], T)
            if np.amax(der) > 2.5:
                series_der.append(der)
                labels_der.append(f'T`{sensor_numbers[i]}')
                series.append(get_sensor_series_from_dataframe(df, start_index, offset, sensor_numbers[i]))
                labels.append(f'T#{sensor_numbers[i]}')
                series.append(get_difference_between_average_and_sensor_temperature(df, data, start_index, offset, sensor_numbers[i]))
                labels.append(f'dT#{sensor_numbers[i]}')
                series.append(data[i])
                labels.append(f'Tmean row#{i}')
        if len(labels) > 0:
            # visualisation
            visualisation.visualisation(os.path.join(config.visualisation_dir, f'{file_name[:-4]}_{column}-{rows}.png'),
                                    np.arange(start_index, start_index + offset),
                                    series,
                                    labels,
                                    f'{file_name}_{start_index}-{start_index + offset}',
                                    'time',
                                    'temp, °C')
            visualisation.visualisation(os.path.join(config.visualisation_dir, f'{file_name[:-4]}_{column}-{rows}_d.png'),
                                        np.arange(start_index, start_index + offset, T),
                                        series_der,
                                        labels_der,
                                        f'{file_name}_{start_index}-{start_index + offset}',
                                        'time',
                                        'temp, °C')
