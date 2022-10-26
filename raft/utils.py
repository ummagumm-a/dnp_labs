def parse_conf(conf_path: str) -> dict[int, str]:
    """
    Takes path to config file as input and produces a dictionary in format: <server_id>: (<server_address>:<server_port>)
    Expects the following format of config file: each line is <server_id> <server_address> <server_port>.

    :param conf_path: path to config file.
    :returns: a dictionary describing nodes in the system.
    """

    def create_entry(line):
        server_id, address, port = line.split()
        return int(server_id), f'{address}:{port}'

    with open(conf_path, 'r') as config_file:
        config_contents = config_file.read()
        lines = config_contents.split('\n')
        entries = list(map(create_entry, lines))

        config_dict = dict(entries)

    return config_dict
