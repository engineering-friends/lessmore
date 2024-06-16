from jinja2 import Environment, FileSystemLoader


def render_jinja2_template(template: str, **kwargs):
    # - Set up the environment and loader

    env = Environment(loader=FileSystemLoader(".."))

    # - Create a  template

    template = env.from_string(template)

    # - Render the template with the provided name or use the default "World"

    return template.render(**kwargs)


def test():
    template = """Hello {{ name | default("World") }}!"""
    assert render_jinja2_template(template, name="John Doe") == "Hello John Doe!"
    assert render_jinja2_template(template) == "Hello World!"


if __name__ == "__main__":
    test()
