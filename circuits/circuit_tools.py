from datetime import datetime


def file_tagger(filename: str) -> str:

    filename += "_" + datetime.now().strftime("%Y_%m_%d-%H_%M_%S")

    return filename
