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

extract_links_jsonl() {
    local jsonl_file="$1"  # Path to the JSONL file

    if ! command -v jq &> /dev/null; then
        echo "Error: jq is not installed. Please install it and try again."
        return 1
    fi

    local link_attribute="$2"
    local links

    links=$(jq -r ".$link_attribute // empty" "$jsonl_file" | paste -sd "," -)

    echo "$links"
}


#
#run_spider "imdb" "-a iterations=1" "data/imdb.json"
#
#start_urls=$(get_start_urls "data/imdb.json")
#
#for url in $start_urls; do
#    echo "$start_url"
#    run_spider 'imdb_movie' "-a start_url=$url" "data/imdb_movie.jsonl"
#done
#
#meta_links=$(extract_links_jsonl data/imdb_movie.jsonl "meta_link")
#
#run_spider "metacritic" "-a start_urls=${meta_links}" "data/metacritic.json"

box_office_links=$(extract_links_jsonl data/imdb_movie.jsonl "box_office_link")

run_spider "box_office" "-a start_urls=${box_office_links}" "data/box_office.json"

echo "Done"
