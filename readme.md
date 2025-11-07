# A simple idiom wordle solver for game "猜成语" provided by "AI晴雅"

## How to use

- Make sure you have Python installed on your computer.
- Install the required packages: fastapi, tqdm
- Install npm packages by running `npm install` in the `idiom-wordle` directory.
- Use a terminal to start backend service using 
  ```bash
  uvicorn main:app --reload --port 8000 
  ```
- Use another terminal to run the frontend service using
  ```bash
  cd idiom-wordle
  npm run dev
  ```
  Then go to http://localhost:5173, You'll see the page.


## Todo
- [ ] The tone of character "一" may differs in different idioms, need to handle this case.
- [ ] The rhyme like "iong" is same as "ong" in Chinese, need to handle this case.