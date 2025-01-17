#!/bin/bash
# Semen
# This is the script that
run_spider() {
    spider_name=$1
    params=$2
    output_file=$3
    echo "Spider started: scrapy crawl $spider_name $params -o $output_file"
    eval "scrapy crawl $spider_name $params -o $output_file"
}

get_start_urls() {
    start_urls=$(jq -r '.url' "$1")
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

iterations_number=$1
result_folder=$2


run_spider "imdb" "-a iterations=$iterations_number" "$result_folder/imdb.jsonl"

start_urls=$(get_start_urls "$result_folder/imdb.jsonl")

for url in $start_urls; do
    echo "${url}"
    run_spider 'imdb_movie' "-a start_url=$url" "$result_folder/imdb_movie.jsonl"
done

meta_links=$(extract_links_jsonl "$result_folder/imdb_movie.jsonl" "meta_link")

run_spider "metacritic" "-a start_urls=$meta_links" "$result_folder/metacritic.jsonl"

box_office_links=$(extract_links_jsonl "$result_folder/imdb_movie.jsonl" "box_office_link")

run_spider "box_office" "-a start_urls=$box_office_links" "$result_folder/box_office.jsonl"

echo "Done"
