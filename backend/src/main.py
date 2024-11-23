
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
  return {"message": "Hello World"}

test_map = """######################
#                    #
#                    #
#                    #
#                    #
#                    #
#                    #
#                    #
#                    #
#                    #
#                    #
#                    #
######################"""
print("test_map: ")
print(test_map)

@app.get("/map")
async def map():
  return {"message": test_map}
