# To run scraper 

```
cd scraper
bash scrap_script.sh <number of pages by 50> <result folder>
```

# To run data preparation file 
```
docker compose up -d --build
cd preparation_module
python preparation.py <1 file> <2 file> <3 file>
```