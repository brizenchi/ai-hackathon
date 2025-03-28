# ai-hackathon
liangcang ai hackathon
### run
```sh
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app/main.py
```
### test
```sh
curl --location --request POST 'http://127.0.0.1:8000/api/v1/chat' \
--header 'Content-Type: application/json' \
--data-raw '{
    "messages":"who r u"
}'
```
