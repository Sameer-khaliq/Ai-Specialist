def main():
    print("Hello from ai-specialist!")

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "Day 1 complete", "stack": "ready"}
if __name__ == "__main__":
    main()
