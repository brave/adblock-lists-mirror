import { createSQLiteThread, createHttpBackend } from 'sqlite-wasm-http';

async function main() {
    const searchInput = document.getElementById('search-input');
    const searchButton = document.getElementById('search-button');
    const statusEl = document.getElementById('status');
    const resultsEl = document.getElementById('results');

    statusEl.textContent = 'Loading database...';

    try {
        const httpBackend = createHttpBackend({
            maxPageSize: 32768,
            timeout: 10000
        });

        const db = await createSQLiteThread({ http: httpBackend });
        const dbUrl = new URL(window.config.dbUrl, window.location.href).href;

        await db('open', {
            filename: dbUrl,
            vfs: 'http'
        });

        // Eagerly check the database connection to catch 404s or corruption on load.
        await db('exec', { sql: "SELECT name FROM sqlite_master WHERE type='table' AND name='rules'" });

        statusEl.textContent = 'DB ready for queries.';

        const search = async () => {
            const query = searchInput.value.trim();
            if (!query) {
                resultsEl.innerHTML = '<p>Please enter a search term.</p>';
                return;
            }

            const searchStartTime = performance.now();
            resultsEl.innerHTML = '<p>Searching...</p>';

            try {
                const ftsQuery = `"${query.replace(/"/g, '""')}"`;

                const searchQuery = `
                    SELECT
                      rc.rule,
                      sf.filename as source_file,
                      rc.line_number
                    FROM rules
                    JOIN rules_content rc ON rules.rowid = rc.id
                    JOIN source_files sf ON rc.source_file_id = sf.id
                    WHERE rules MATCH ?
                    ORDER BY rank
                    LIMIT 50;
                `;

                const rows = [];
                await db('exec', {
                    sql: searchQuery,
                    bind: [ftsQuery],
                    callback: (result) => {
                        if (result.row) {
                            rows.push(result.row);
                        }
                    }
                });

                if (rows.length === 0) {
                    const searchEndTime = performance.now();
                    const searchDuration = ((searchEndTime - searchStartTime) / 1000).toFixed(3);
                    resultsEl.innerHTML = `<p>No results found. <span class="timing-info">(Search took ${searchDuration}s)</span></p>`;
                    return;
                }

                const summaryDiv = document.createElement('div');
                summaryDiv.className = 'search-summary';
                summaryDiv.innerHTML = `Found ${rows.length} results:`;
                resultsEl.innerHTML = '';
                resultsEl.appendChild(summaryDiv);

                for (const row of rows) {
                    const item = document.createElement('div');
                    item.className = 'result-item';

                    const rule = row[0];
                    const source_file = row[1];
                    const line_number = row[2];

                    const githubUrl = `https://github.com/brave/adblock-lists-mirror/blob/lists/lists/${source_file}#L${line_number}`;

                    item.innerHTML = `
                        <pre>${rule}</pre>
                        <a href="${githubUrl}" target="_blank">
                            ${source_file} (line ${line_number})
                        </a>
                    `;
                    resultsEl.appendChild(item);
                }

                const searchEndTime = performance.now();
                const searchDuration = ((searchEndTime - searchStartTime) / 1000).toFixed(3);
                summaryDiv.innerHTML = `Found ${rows.length} results <span class="timing-info">in ${searchDuration}s</span>:`;

            } catch (searchErr) {
                console.error('Search error:', searchErr);

                const errorMessage = (searchErr.result && searchErr.result.message) || searchErr.message || '';

                if (errorMessage.includes('404') ||
                    errorMessage.includes("Couldn't load") ||
                    errorMessage.includes('SQLITE_CORRUPT') ||
                    errorMessage.includes('SQLITE_NOTADB')) {
                    statusEl.innerHTML = 'The database file appears to be corrupted. <a href="#" onclick="location.reload(); return false;">Please reload the page.</a>';
                    resultsEl.innerHTML = '';
                    searchInput.disabled = true;
                    searchButton.disabled = true;
                } else {
                    resultsEl.textContent = `Search error: ${errorMessage}`;
                }
            }
        };

        searchButton.addEventListener('click', search);
        searchInput.addEventListener('keyup', (e) => {
            if (e.key === 'Enter') {
                search();
            }
        });

    } catch (err) {
        console.error('Database initialization error:', err);
        const errorMessage = (err.result && err.result.message) || err.message || '';

        if (errorMessage.includes('404') ||
            errorMessage.includes("Couldn't load") ||
            errorMessage.includes('SQLITE_CORRUPT') ||
            errorMessage.includes('SQLITE_NOTADB')) {
            statusEl.innerHTML = 'The database file is unavailable. <a href="#" onclick="location.reload(); return false;">Please reload the page.</a>';
        } else {
            statusEl.textContent = `Error loading database: ${errorMessage}`;
        }
        searchButton.disabled = true;
        searchInput.disabled = true;
        searchInput.placeholder = "Database unavailable";
    }
}

main();
