from __future__ import annotations


def ask_for_option(prompt: str, options: list[str]) -> str:
    while True:
        print(prompt + ":")
        for index, option in enumerate(options, start=1):
            print(f"  {index}. {option}")
        choice = input("> ")
        option = _parse_option(choice, options)
        if option is not None:
            return option
        print("Please enter a valid option number.")


def ask_for_integer(prompt: str, min_value: int, max_value: int) -> int:
    while True:
        choice = input(f"{prompt} [{min_value}-{max_value}]: ")
        value = _parse_integer(choice)
        if value is not None and min_value <= value <= max_value:
            return value
        print("Please enter a valid integer in range.")


def _parse_option(choice: str, options: list[str]) -> str | None:
    value = _parse_integer(choice)
    if value is None:
        return None
    if value < 1 or value > len(options):
        return None
    return options[value - 1]


def _parse_integer(choice: str) -> int | None:
    try:
        return int(choice)
    except ValueError:
        return None
