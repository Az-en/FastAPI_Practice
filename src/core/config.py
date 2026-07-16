import os
from dotenv import load_dotenv
load_dotenv()

SECRET = os.getenv("SECRET")


# if __name__ == "__main__":
#     print(SECRET)