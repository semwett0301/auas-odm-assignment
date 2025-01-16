#!/bin/bash

run_spider() {
    spider_name=$1
    params=$2
    output_file=$3
    echo "Запуск паука: scrapy crawl $spider_name $params -O $output_file"
    eval "scrapy crawl $spider_name $params -O $output_file"
}

get_start_urls() {
    start_urls=$(jq -r '.[].url' "$1")
    echo "$start_urls"
}

run_spider "imdb" "-a iterations=1" "imdb.json"

start_urls=$(get_start_urls "imdb.json")

for url in $start_urls; do
    echo "$start_url"
    run_spider 'imdb_movie' "-a start_url=$url" "imdb_movie.json"
done

echo "Done"
