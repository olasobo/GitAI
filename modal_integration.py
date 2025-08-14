import modal

app = modal.App("gitai")

@app.function()
def example(x):
    return x * x

@app.local_entrypoint()
def main():
    print(example.remote(2))
    