from ef_bots.ef_threads.ef_threads import EfThreads


async def main(env="test"):
    async with EfThreads(env=env).stack() as ef_threads:
        await ef_threads.run()


if __name__ == "__main__":
    import typer

    typer.run(main)
