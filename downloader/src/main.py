import fire
from consumer import run_listener


def consumer(bootstrap_server, topic):
    run_listener(bootstrap_server, topic)


if __name__ == '__main__':
    fire.Fire()
