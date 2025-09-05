import typer

app = typer.Typer()

@app.command()
def runserver():
    """
    Runs the development server.
    """
    print("Starting server...")

if __name__ == "__main__":
    app()
