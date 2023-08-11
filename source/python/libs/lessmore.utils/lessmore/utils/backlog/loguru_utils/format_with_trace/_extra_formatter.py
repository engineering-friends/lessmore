def _extra_formatter(record, fancy=True):
    if fancy:

        values = []
        for i, (k, v) in enumerate(record["extra"]["_extra"].items()):
            values.append(
                ": ".join(
                    [
                        f"<magenta>{{extra[_extra_{2 * i}]}}</magenta>",
                        f"<yellow>{{extra[_extra_{2 * i + 1}]}}</yellow>",
                    ]
                )
            )
            record["extra"][f"_extra_{2 * i}"] = k
            record["extra"][f"_extra_{2 * i + 1}"] = v
        return ", ".join(values)

    return "<yellow>{extra[_extra]}</yellow>"


# see test at format_with_trace.py
