from fastapi import FastAPI

app = FastAPI();

@app.post('/test')
def test_endpoint():
    return {'Satatus':'Successfull'}

@app.post('/risk_calculation')
def risk_calculation():
    pass
