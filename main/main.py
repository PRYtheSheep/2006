from website.routers.views import set_app
from website import create_app, register

app = create_app()

if __name__ == "__main__":
    app = register(app)
    set_app(app)
    app.run(debug=True)
