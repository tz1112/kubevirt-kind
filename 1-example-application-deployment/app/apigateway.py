# https://realpython.com/fastapi-python-web-apis/
# https://stackoverflow.com/questions/71413203/how-to-send-and-receive-data-in-xml-format-using-websockets-in-fastapi

# run with uvicorn apigateway:app --reload


from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import FileResponse
import uvicorn
import shutil

app = FastAPI()

@app.get("/helloworld")
async def firsttest():
    return {"message" : "hello world from fastapi"}

@app.post("/generate")
async def generate(request: Request):
    content_type = request.headers['Content-Type']
    if content_type == 'application/xml':
        body = await request.body()
        body = str(body).replace("</a>", "testitest")
        return Response(content=body, media_type="application/xml")
    else:
        raise HTTPException(status_code=400, detail=f'Content type {content_type} not supported')
    
# creting zip is synchronous, do not use async def here    
@app.post("/compile")
def compile(request: Request):
    content_type = request.headers['Content-Type']
    if content_type == 'applicatieon/xml':
        shutil.make_archive("CompRes", 'zip', "res")
        return FileResponse("CompRes.zip")
    else:
        raise HTTPException(status_code=400, detail=f'Content type {content_type} not supported')
    

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)    