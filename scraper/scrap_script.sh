#!/bin/bash

run_spider() {
    spider_name=$1
    params=$2
    output_file=$3
    echo "Запуск паука: scrapy crawl $spider_name $params -o $output_file"
    eval "scrapy crawl $spider_name $params -o $output_file"
}

get_start_urls() {
    start_urls=$(jq -r '.[].url' "$1")
    echo "$start_urls"
}

extract_meta_links_jsonl() {
    local jsonl_file="$1"  # Path to the JSONL file

    # Check if jq is installed
    if ! command -v jq &> /dev/null; then
        echo "Error: jq is not installed. Please install it and try again."
        return 1
    fi

    # Extract meta_link fields and join them with commas
    local meta_links
    meta_links=$(jq -r '.meta_link // empty' "$jsonl_file" | paste -sd "," -)

    echo "$meta_links"
}



run_spider "imdb" "-a iterations=1" "data/imdb.json"

start_urls=$(get_start_urls "data/imdb.json")

for url in $start_urls; do
    echo "$start_url"
    run_spider 'imdb_movie' "-a start_url=$url" "data/imdb_movie.jsonl"
done

meta_links=$(extract_meta_links_jsonl imdb_movie.jsonl)

run_spider "metacritic" "-a start_urls=${meta_links}" "data/metacritic.json"

echo "Done"
