import time

from celery import Celery
from dash import CeleryManager
from dash_extensions.enrich import (
    DashProxy,
    Input,
    Output,
    RedisBackend,
    Serverside,
    ServersideOutputTransform,
    callback,
    ctx,
    html,
)

from flask_app import create_flask_app

# *** INITIALIZE CELERY ***

REDIS_URL = "redis://127.0.0.1:6379/0"
REDIS_HOST = "127.0.0.1"

celery_app = Celery(__name__, broker=REDIS_URL, backend=REDIS_URL)
background_callback_manager = CeleryManager(celery_app)

# *** INSTANTIATE FLASK APP, AND GRAB THE SERVER ***
server = create_flask_app()

URL_BASE = "/bkgd/"

app = DashProxy(
    __name__,
    server=server,
    routes_pathname_prefix=URL_BASE,
    background_callback_manager=background_callback_manager,
    transforms=[ServersideOutputTransform(backends=[RedisBackend(host=REDIS_HOST)])],
)

app.layout = html.Div(
    [
        html.Div(
            [
                html.P(id="paragraph_id", children=["Button not clicked"]),
                html.Progress(id="progress_bar", value="0"),
            ]
        ),
        html.Button(id="button_id", children="Run Job!"),
        html.Button(id="cancel_button_id", children="Cancel Running Job!"),
    ]
)


@callback(
    output=Output("paragraph_id", "children"),
    inputs=Input("button_id", "n_clicks"),
    background=True,  # triggers dash to use background callbacks here
    running=[
        (Output("button_id", "disabled"), True, False),
        (Output("cancel_button_id", "disabled"), False, True),
        (
            Output("paragraph_id", "style"),
            {"visibility": "hidden"},
            {"visibility": "visible"},
        ),
        (
            Output("progress_bar", "style"),
            {"visibility": "visible"},
            {"visibility": "hidden"},
        ),
    ],
    cancel=Input("cancel_button_id", "n_clicks"),
    progress=[Output("progress_bar", "value"), Output("progress_bar", "max")],
    prevent_initial_call=True,
)
def update_progress(set_progress, n_clicks):
    total = 5
    print("\n\nUpdating progress!!!\n\n")
    print(ctx.triggered)  # pressing cancel button doesn't trigger anything
    for i in range(total + 1):
        set_progress((str(i), str(total)))
        time.sleep(1)

    return f"Clicked {n_clicks} times"


app.register_celery_tasks()  # required for dash_extensions to use celery

if __name__ == "__main__":
    app.run(debug=True)
