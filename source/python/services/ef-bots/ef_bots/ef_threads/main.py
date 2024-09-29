import asyncio

from ef_bots.ef_threads.ef_threads import EfThreads


async def main(env: str):
    async with EfThreads.stack(env=env) as ef_threads:
        await ef_threads.run()


if __name__ == "__main__":
    import fire

    def sync_main(env: str = "test"):
        asyncio.run(main(env=env))

    fire.Fire(sync_main)
