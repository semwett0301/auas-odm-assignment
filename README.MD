# AUAS ODM Assignment - Movie Data Scraping & Analysis Platform

A comprehensive web scraping and data analysis platform for collecting movie data from multiple sources including IMDb, Metacritic, and Box Office Mojo. The system scrapes movie information, processes the data, and stores it in a PostgreSQL database for analysis.

## 🚀 Tech Stack

### Backend & Data Processing
- **Python 3.x** - Core programming language
- **Scrapy** - Web scraping framework
- **Selenium** - Browser automation for dynamic content
- **Pandas** - Data manipulation and analysis
- **NumPy** - Numerical computing
- **SQLAlchemy** - Database ORM
- **psycopg2** - PostgreSQL adapter

### Database
- **PostgreSQL 14** - Primary database
- **Docker** - Containerization

### Data Visualization & Analysis
- **Plotly** - Interactive data visualization
- **Matplotlib** - Static plotting
- **Seaborn** - Statistical data visualization
- **SciPy** - Scientific computing

### Data Storage & Processing
- **FastParquet** - Parquet file format support
- **PyArrow** - Columnar data processing
- **JSONL** - JSON Lines format for scraped data

### DevOps & Deployment
- **Docker Compose** - Multi-container orchestration
- **Bash Scripting** - Automation scripts

## 📁 Project Structure

```
auas-odm-assignment/
├── docker-compose.yml          # Database container configuration
├── init.sql                    # Database schema initialization
├── requirements.txt            # Python dependencies
├── README.MD                   # This file
├── scraper/                    # Web scraping module
│   ├── scrap_module/          # Scrapy project
│   │   ├── spiders/           # Individual spider implementations
│   │   │   ├── imdb.py        # IMDb movie list scraper
│   │   │   ├── imdb_movie.py  # Individual movie details scraper
│   │   │   ├── metacritic.py  # Metacritic reviews scraper
│   │   │   └── box_office.py  # Box office data scraper
│   │   ├── items.py           # Data item definitions
│   │   ├── pipelines.py       # Data processing pipelines
│   │   ├── middlewares.py     # Request/response middleware
│   │   └── settings.py         # Scrapy configuration
│   ├── preparation_module/    # Data preparation and ETL
│   │   ├── prepare.py         # Main data processing script
│   │   ├── settings.py        # Database configuration
│   │   └── utils.py           # Utility functions
│   ├── data/                  # Scraped data storage
│   │   ├── imdb.jsonl         # IMDb movie URLs
│   │   ├── imdb_movie.jsonl   # Movie details
│   │   ├── metacritic.jsonl   # Metacritic reviews
│   │   └── box_office.jsonl   # Box office data
│   ├── scrap_script.sh        # Automated scraping script
│   └── scrapy.cfg             # Scrapy project configuration
└── utils/                     # Shared utilities
```

## 🛠️ Installation & Setup

### Prerequisites
- Docker and Docker Compose
- Python 3.x
- Git

### 1. Clone the Repository
```bash
git clone <repository-url>
cd auas-odm-assignment
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start Database
```bash
docker compose up -d --build
```

### 4. Verify Database Connection
The PostgreSQL database will be available at `localhost:5432` with:
- Username: `postgres`
- Password: `postgres`
- Database: `postgres`

## 🚀 Usage

### Running the Scraper

1. **Navigate to scraper directory**:
```bash
cd scraper
```

2. **Run the automated scraping script**:
```bash
bash scrap_script.sh <number_of_pages> <result_folder>
```

**Parameters**:
- `number_of_pages`: Number of IMDb pages to scrape (each page contains ~50 movies)
- `result_folder`: Directory to store scraped data files

**Example**:
```bash
bash scrap_script.sh 10 ./data
```

This will:
1. Scrape IMDb movie lists
2. Extract individual movie details
3. Collect Metacritic reviews
4. Gather box office data
5. Save all data as JSONL files

### Data Processing & Database Import

1. **Navigate to preparation module**:
```bash
cd preparation_module
```

2. **Run data preparation script**:
```bash
python prepare.py <metacritic_file> <imdb_movie_file> <box_office_file>
```

**Example**:
```bash
python prepare.py ../data/metacritic.jsonl ../data/imdb_movie.jsonl ../data/box_office.jsonl
```

This will:
1. Clean and normalize the scraped data
2. Establish relationships between entities
3. Import data into PostgreSQL database
4. Create proper foreign key relationships

## 📊 Database Schema

The system creates the following tables:

- **movie**: Core movie information
- **genre**: Movie genres
- **movie_genre**: Many-to-many relationship between movies and genres
- **company**: Production companies
- **movie_company**: Movie-company relationships
- **person**: Cast and crew members
- **movie_cast**: Movie-person relationships
- **region**: Geographic regions
- **region_income**: Box office performance by region
- **release**: Release information and financial data
- **review**: User and critic reviews
- **movie_parents_summary**: Parental guidance ratings

## 🔧 Configuration

### Database Settings
Edit `preparation_module/settings.py` to configure database connection:
```python
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "postgres"
POSTGRES_URL = "localhost"
POSTGRES_PORT = "5432"
POSTGRES_DB = "postgres"
```

### Scrapy Settings
Modify `scrap_module/settings.py` for scraping configuration:
- User agents
- Download delays
- Concurrent requests
- Middleware settings