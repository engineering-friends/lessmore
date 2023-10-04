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
            ("Поза воина", "2m"),
            ("Наклон", "2m"),
            ("Бабочка", "2m"),
            ("Намасте сзади", "2m"),
            ("Шпагат П", "2m"),
            ("Шпагат Л", "2m"),
            ("Шпагат боковой", "2m"),
            ("Голубь П", "2m"),
            ("Голубь Л", "2m"),
            ("Мостик", "2m"),
        ]
    )

    write_file(board, "yoga.mtb")


if __name__ == "__main__":
    test()
