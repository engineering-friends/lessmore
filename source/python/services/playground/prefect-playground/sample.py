from prefect import Flow, flow, task


@task
def fetch_data():
    # Imagine fetching data from an API or database
    return {"data": [1, 2, 3, 4, 5]}


@task
def process_data(data):
    # Simple data processing
    return [i * 2 for i in data["data"]]


@task
def store_results(results):
    # Imagine storing results in a file or database
    print("Results stored:", results)


@flow(log_prints=True)
def hello_world():
    data = fetch_data()
    processed_data = process_data(data)
    store_results(processed_data)


if __name__ == "__main__":
    hello_world.serve(name="my-first-deployment", tags=["onboarding"], parameters={}, interval=60)
