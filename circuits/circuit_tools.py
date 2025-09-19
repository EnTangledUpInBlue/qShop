from datetime import datetime


def file_tagger(filename: str) -> str:
    r"""
    Method for adding a date and time tag onto
    filenames intended for data collection
    from simulations.

    :param filename:

    :return:
    """

    filename += "_" + datetime.now().strftime("%Y_%m_%d-%H_%M_%S")

    return filename


def repetition_encoding_schedule(block: list[int]) -> list[list[tuple[int]]]:
    r"""
    Method for producing a scheduling of CNOT gates
    in the encoding circuit as a sequence of lists
    of tuples representing the rounds of the
    schedule.

    :param block:

    :return:
    """

    n = len(block)
    mark = int(n / 2)

    first_half = block[:mark]
    second_half = block[mark:]

    schedule = [[(first_half[0], second_half[0])]]

    for jj in range(mark - 1):
        round = []
        round.append((first_half[jj], first_half[jj + 1]))
        round.append((second_half[jj], second_half[jj + 1]))
        schedule.append(round)

    if n % 2:
        schedule.append([(second_half[-2], second_half[-1])])

    return schedule


def repetition_measurement_schedule(block: list[int]) -> list[list[tuple[int]]]:
    r"""
    Method for producing a scheduling of CNOT gates
    in the measurement as a sequence of lists
    of tuples representing the rounds of the
    schedule.

    :param block:

    :return:
    """

    n = len(block)
    mark = int(n / 2)

    schedule = []

    first_half = block[:mark]
    second_half = block[mark:]

    for jj in range(1, mark):
        round = []
        round.append((first_half[-jj - 1], first_half[-jj]))
        round.append((second_half[-jj - 1], second_half[-jj]))
        schedule.append(round)

    if n % 2:
        schedule.append([(second_half[0], second_half[1])])

    finalround = [(first_half[0], second_half[0])]

    schedule.append(finalround)

    return schedule
