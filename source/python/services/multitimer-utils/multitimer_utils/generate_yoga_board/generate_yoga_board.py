from deeplay.utils.unified import TimedeltaLike, to_seconds
from multitimer_utils.render_jinja2_template import render_jinja2_template

from lessmore.utils.file_helpers.read_file import read_file
from lessmore.utils.file_helpers.write_file import write_file


def generate_yoga_board(label_and_times: list[tuple[str, TimedeltaLike]]):  # [("work", 25), ("rest", 5)]
    return render_jinja2_template(
        read_file("yoga_board_template.xml"),
        interval_timer=render_jinja2_template(
            read_file("interval_timer_template.xml"),
            items="\n".join(
                [
                    render_jinja2_template(
                        read_file("item_template.xml"),
                        label=label,
                        time=float(to_seconds(time)),
                    )
                    for label, time in label_and_times
                ]
            ),
            key="k3",
        ),
        name="Yoga",
    )


def test():
    board = generate_yoga_board(
        label_and_times=[
            ("Разминка груди", "3m"),
            ("Массаж предплеч", "3m"),
            ("Массаж груди", "3m"),
            ("Намасте сзади", "3m"),
            ("Кошка", "3m"),
            ("Кошка на локтях", "3m"),
            ("Посох", "3m"),
            ("Шпагат боковой", "3m"),
            ("Обнимание колена П", "3m"),
            ("Обнимание колена Л", "3m"),
            ("Шпагат П", "3m"),
            ("Шпагат Л", "3m"),
            ("Массаж ног", "3m"),
            ("Массаж икр", "3m"),
            ("Собака", "3m"),
            ("Растяжка берда П", "3m"),
            ("Растяжка берда Л", "3m"),
            ("Наклон", "3m"),
            ("Икры П", "3m"),
            ("Икры Л", "3m"),
            ("Воин П", "3m"),
            ("Воин Л", "3m"),
            ("Couch stretch", "3m"),
            ("Calf stretch R", "3m"),
            ("Calf stretch L", "3m"),
            ("Hamstring stretch R", "3m"),
            ("Hamstring stretch L", "3m"),
            ("Eye of the needle R", "3m"),
            ("Eye of the needle L", "3m"),
            ("Groin stretch", "3m"),
        ]
    )

    write_file(board, "yoga.mtb")


if __name__ == "__main__":
    test()
