import configparser


# turn a config map into a dictionary
def get_configuration(filename):

    config = configparser.ConfigParser()
    config.read(filename)

    all_sections = dict()
    for section in config.sections():
        dict1 = {}
        options = config.options(section)
        for option in options:
            try:
                dict1[option] = config.get(section, option)
            except:
                dict1[option] = None
        all_sections[section] = dict1

    return all_sections
