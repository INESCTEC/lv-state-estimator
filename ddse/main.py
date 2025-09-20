from fastapi import FastAPI

import ddse.routers as rt

app = FastAPI(
    title="DDSE-OS",
    description="""
    The Data-driven State Estimator (DdSE) is a tool specially designed to provide a
    real-time snapshot of the low voltage network comprising voltage magnitudes for all
    the meters capable of gathering historical data.
    The methodology takes advantage of information gathered by the smart grid
    infrastructure along with some real-time measurements and exogenous information
    like weather forecasts and calendar information (hour of the day, day of the week, etc.),
    while avoiding full knowledge about network topology and electrical characteristics.
    """,
    version="0.1",
    contact={
        "name": "INESCTEC - Centro de Produção Energia e Sistemas (CPES)",
        "url": "https://www.inesctec.pt/",
    },
    license_info={
        "name": "GNU Affero General Public License v3.0",
        "url": "https://www.gnu.org/licenses/agpl-3.0.txt",
    },
    root_path="/",
)


@app.get("/")
async def root():
    return {"message": "Welcome to the DdSE application.."}


app.include_router(rt.grid.router, prefix="/grid")
app.include_router(rt.historical.router, prefix="/historical")
app.include_router(rt.state_estimation.router, prefix="/se")
