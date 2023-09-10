from deeplay.utils.unified import TimedeltaLike, to_seconds
from multitimer_utils.render_jinja2_template import render_jinja2_template

from lessmore.utils.file_helpers.read_file import read_file
from lessmore.utils.file_helpers.write_file import write_file


def build_yoga_board(label_and_times: list[tuple[str, TimedeltaLike]]):  # [("work", 25), ("rest", 5)]
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
    board = build_yoga_board(
        label_and_times=[
            # - Massage
            ("Само-массаж", "15m"),
            # - ATG pack
            ("Couch stretch R", "3m"),
            ("Couch stretch L", "3m"),
            ("Calf stretch R", "3m"),
            ("Calf stretch L", "3m"),
            ("Hamstring stretch R", "3m"),
            ("Hamstring stretch L", "3m"),
            ("Eye of the needle R", "3m"),
            ("Eye of the needle L", "3m"),
            ("Groin stretch", "3m"),
            # - Legs
            ("Воин Л", "3m"),
            ("Бабочка", "3m"),
            # - Yoga classics
            ("Кошка", "5m"),
            ("Собака", "3m"),
            # - Chest opener
            ("Намасте сзади", "3m"),
            # - Splits
            ("Обнимание колена П", "3m"),
            ("Обнимание колена Л", "3m"),
            ("Шпагат П", "3m"),
            ("Шпагат Л", "3m"),
            ("Шпагат боковой", "8m"),
        ]
    )

    write_file(board, "yoga.mtb")


if __name__ == "__main__":
    test()
