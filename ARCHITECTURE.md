# CityU Curriculum Scraper - Architecture Documentation

## Overview
This project follows a layered architecture pattern with clear separation of concerns. The orchestrator (`orchestrator.py`) acts as a thin CLI layer that only handles argument parsing and delegates all business logic to specialized modules in the `core/` directory.

## Architecture Layers

```
orchestrator.py (CLI Layer)
    ↓
core/ (Business Logic Layer)
    ├── scraper/      - Web scraping and caching
    ├── filter/       - Course filtering logic
    ├── dp_build/     - Data processing and export
    ├── vis/          - Graph visualization
    └── config.py     - Configuration management
```

## Directory Structure

```
cityu cuirrculum/
├── orchestrator.py           # CLI entry point (thin layer)
├── core/
│   ├── config.py            # TOML config loading
│   ├── scraper/
│   │   ├── __init__.py
│   │   ├── cache.py         # HTML caching utilities
│   │   ├── fetch.py         # HTTP fetching (existing)
│   │   ├── parse.py         # HTML parsing (existing)
│   │   └── major_scraper.py # High-level scraping orchestration
│   ├── filter/
│   │   ├── __init__.py
│   │   └── check.py         # Course filtering by allowed codes
│   ├── dp_build/
│   │   ├── __init__.py
│   │   ├── export.py        # JSON/CSV export
│   │   └── db_builder.py    # SQLite DB construction
│   └── vis/
│       ├── __init__.py
│       └── graph.py         # Dependency & roots visualization (existing)
├── config/
│   ├── cityu.toml                    # Main config with bilingual comments
│   ├── visualize_dependency.toml     # Dependency graph preset
│   └── visualize_roots.toml          # Roots-only graph preset
└── outputs/
    ├── courses.db                    # SQLite database
    └── vNNN/                         # Versioned outputs (v001, v002, etc.)
        ├── dependency_vNNN.png
        └── roots_only_vNNN.png
```

## Module Responsibilities

### orchestrator.py (CLI Layer)
**Responsibilities:**
- Parse command-line arguments using `argparse`
- Load configuration files (TOML)
- Merge config defaults with CLI arguments
- Call appropriate core module functions
- Handle command routing (scrape-major, build-db, visualize, etc.)

**Does NOT contain:**
- Business logic
- Data processing
- File I/O (except config loading)
- Database operations
- Network requests

### core/scraper/
**Modules:**
- `fetch.py` - HTTP requests with retry logic
- `parse.py` - BeautifulSoup HTML parsing
- `cache.py` - HTML caching to disk
- `major_scraper.py` - High-level scraping workflow

**Responsibilities:**
- Fetch HTML from URLs
- Parse major curriculum pages
- Parse course detail pages
- Cache HTML responses
- Extract course information

### core/filter/
**Modules:**
- `check.py` - Course filtering logic

**Responsibilities:**
- Load allowed course codes from file
- Filter SQLite database to remove non-allowed courses
- Maintain referential integrity after filtering

### core/dp_build/
**Modules:**
- `export.py` - Data export utilities
- `db_builder.py` - Database construction

**Responsibilities:**
- Convert scraped data to JSON/CSV
- Build SQLite database from scraped courses
- Create tables (courses, prerequisites, exclusions)
- Insert course data with proper foreign keys

### core/vis/
**Modules:**
- `graph.py` - Graph rendering

**Responsibilities:**
- Render dependency trees using networkx/matplotlib
- Generate roots-only graphs (courses with no prerequisites and no dependents)
- Apply visualization settings (layering, coloring, truncation, etc.)
- Support focus mode, cycle highlighting, isolation exclusion

### core/config.py
**Responsibilities:**
- Load TOML configuration files
- Support profile-based configs (dependency/roots presets)
- Auto-discover default config paths
- Provide bilingual comment support

## Command Flow Examples

### 1. scrape-major Command
```
User runs: python orchestrator.py scrape-major --url <URL> --out data.json

Flow:
orchestrator.cmd_scrape_major()
  → scrape_major_pages(urls, **opts)  [core/scraper/major_scraper.py]
    → fetch_html()                     [core/scraper/fetch.py]
    → parse_major_page()               [core/scraper/parse.py]
    → maybe_read_cache()               [core/scraper/cache.py]
  → save_json(results, path)           [core/dp_build/export.py]
```

### 2. build-db Command
```
User runs: python orchestrator.py build-db --major-url <URL> --db courses.db

Flow:
orchestrator.build_db()
  → build_course_db(url, db_path, **opts)  [core/dp_build/db_builder.py]
    → scrape_major_pages()                  [core/scraper/major_scraper.py]
    → CREATE TABLE courses, prerequisites, exclusions
    → INSERT scraped data with regex parsing
```

### 3. visualize Command
```
User runs: python orchestrator.py visualize --profile dependency --bundle-version

Flow:
orchestrator.cmd_visualize()
  → load_config()                           [core/config.py]
  → filter_db_by_allowed() if configured    [core/filter/check.py]
  → render_dependency_tree()                [core/vis/graph.py]
  → render_root_courses()                   [core/vis/graph.py]
```

## Configuration System

### Config File Hierarchy
1. **Explicit `--config` flag**: Overrides all
2. **Profile configs**: `config/visualize_<profile>.toml` when `--profile` is used
3. **Default config**: `config/cityu.toml` if exists
4. **CLI arguments**: Always override config values

### Config Sections
```toml
[common]
out_dir = 'outputs'
cache_dir = 'cache'

[scrape_major]
delay = 0.0
timeout = 15.0
concurrency = 1

[build_db]
delay = 0.2
concurrency = 4
reset = false

[visualize]
db = 'outputs/courses.db'
truncate_title = 40
max_per_layer = 16
no_unit_colors = false
bundle_version = true
allowed_courses_file = 'config/allowed_courses.txt'
```

## Key Design Principles

1. **Separation of Concerns**: Each module has a single, well-defined responsibility
2. **Thin Orchestrator**: CLI layer contains no business logic
3. **Reusability**: Core modules can be imported and used independently
4. **Testability**: Pure functions in core modules are easy to unit test
5. **Configuration-Driven**: Behavior controlled via TOML configs, not hardcoded values
6. **Layered Architecture**: Clear data flow from scraper → filter → data → visualization

## Migration Notes

### What Changed
- **Before**: All logic in `orchestrator.py` (600+ lines, tight coupling)
- **After**: Logic extracted to `core/` modules (orchestrator: ~330 lines, pure CLI)

### Modules Created
- `core/scraper/cache.py` - Extracted caching logic
- `core/scraper/major_scraper.py` - Extracted scraping orchestration
- `core/filter/check.py` - Extracted filtering logic
- `core/dp_build/export.py` - Extracted export utilities
- `core/dp_build/db_builder.py` - Extracted DB building logic

### Imports Updated
```python
# Old (in orchestrator.py)
def _maybe_read_cache(...): ...
def _filter_db_by_allowed(...): ...

# New (clean imports)
from core.scraper.cache import maybe_read_cache, write_cache
from core.filter.check import load_allowed_codes, filter_db_by_allowed
```

## Testing Recommendations

### Unit Tests (to be added)
- `test_scraper_cache.py` - Cache read/write operations
- `test_filter_check.py` - Course code filtering logic
- `test_export.py` - JSON/CSV export correctness
- `test_db_builder.py` - Database integrity checks

### Integration Tests
- End-to-end scrape → build-db → visualize workflow
- Config loading with different profiles
- Cache behavior across multiple runs
- Filter layer removing courses correctly

## Future Enhancements

1. **Add async support** for scraper (currently using ThreadPoolExecutor)
2. **Add retry logic** to db_builder for failed course fetches
3. **Add validation layer** between scraper and db_builder
4. **Extract graph layout** into separate module from rendering
5. **Add CLI tests** using pytest with captured stdout/stderr
6. **Add type hints** for all function parameters and returns
7. **Add logging module** to replace print statements

---

**Created**: 2025-01-XX  
**Last Updated**: After architecture refactoring  
**Status**: ✅ Refactoring Complete
