from website import create_app, register

app = create_app()

if __name__ == "__main__":
    app = register(app)
    app.run(debug=True)
