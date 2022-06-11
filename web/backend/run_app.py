import uvicorn
import os

if __name__ == '__main__':
    uvicorn.run("app:app", host=os.environ['HOST'],
                port=int(os.environ['BACKEND_PORT']),
                reload=True, debug=True, workers=3,
                )
