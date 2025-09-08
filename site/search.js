import sqlJsHttpvfs from "https://cdn.jsdelivr.net/npm/sql.js-httpvfs@0.8.12/+esm";
const { createDbWorker } = sqlJsHttpvfs;

async function main() {
    // Workaround for cross-origin worker restrictions
    const workerUrlBlob = await fetch('https://cdn.jsdelivr.net/npm/sql.js-httpvfs@0.8.12/dist/sqlite.worker.js').then(r => r.blob());
    const workerUrl = URL.createObjectURL(workerUrlBlob);

    const wasmUrl = new URL(
        'https://cdn.jsdelivr.net/npm/sql.js-httpvfs@0.8.12/dist/sql-wasm.wasm',
        import.meta.url
    );

    const searchInput = document.getElementById('search-input');
    const searchButton = document.getElementById('search-button');
    const statusEl = document.getElementById('status');
    const resultsEl = document.getElementById('results');

    // Set initial loading status
    statusEl.textContent = 'Loading database...';

    try {
        statusEl.textContent = 'Initializing DB...';

        const worker = await createDbWorker(
            [
                {
                    from: "jsonconfig",
                    configUrl: `${new URL('config.json', window.location.href).href}?t=${Date.now()}`
                }
            ],
            workerUrl,
            wasmUrl.toString()
        );

        // Clean up the blob URL after the worker is created
        URL.revokeObjectURL(workerUrl);

        statusEl.textContent = 'DB ready for queries.';

        const search = async () => {
            const query = searchInput.value.trim();
            if (!query) {
                resultsEl.innerHTML = '<p>Please enter a search term.</p>';
                return;
            }

            // Start timing search
            const searchStartTime = performance.now();
            resultsEl.innerHTML = '<p>Searching...</p>';

            try {
                // To handle special characters in FTS5, wrap the query in double quotes
                // and escape any internal double quotes by doubling them up.
                const ftsQuery = `"${query.replace(/"/g, '""')}"`;

                // Shared query for both EXPLAIN and actual execution
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

                // Log the raw query and parameters
                console.log('Formatted Query:', searchQuery.trim().replace('?', `'${ftsQuery}'`));

                // Explain the query plan before executing
                //const explainResult = await worker.db.query(`EXPLAIN QUERY PLAN ${searchQuery}`, [ftsQuery]);
                //console.log('Query Plan:', explainResult);

                // Execute the actual query
                const results = await worker.db.query(searchQuery, [ftsQuery]);

                if (!results || results.length === 0) {
                    // End timing search for no results case
                    const searchEndTime = performance.now();
                    const searchDuration = ((searchEndTime - searchStartTime) / 1000).toFixed(3);
                    resultsEl.innerHTML = `<p>No results found. <span class="timing-info">(Search took ${searchDuration}s)</span></p>`;
                    return;
                }

                // Create results summary (timing will be added after DOM updates)
                const summaryDiv = document.createElement('div');
                summaryDiv.className = 'search-summary';
                summaryDiv.innerHTML = `Found ${results.length} results:`;
                resultsEl.innerHTML = '';
                resultsEl.appendChild(summaryDiv);

                for (const row of results) {
                    const item = document.createElement('div');
                    item.className = 'result-item';

                    const githubUrl = `https://github.com/brave/adblock-lists-mirror/blob/lists/lists/${row.source_file}#L${row.line_number}`;

                    item.innerHTML = `
              <pre>${row.rule}</pre>
              <a href="${githubUrl}" target="_blank">
                ${row.source_file} (line ${row.line_number})
              </a>
            `;
                    resultsEl.appendChild(item);
                }

                // End timing search after all DOM updates are complete
                const searchEndTime = performance.now();
                const searchDuration = ((searchEndTime - searchStartTime) / 1000).toFixed(3);
                summaryDiv.innerHTML = `Found ${results.length} results <span class="timing-info">in ${searchDuration}s</span>:`;

            } catch (searchErr) {
                console.error('Search error:', searchErr);

                // Check if it's a database loading error (404, etc.)
                if (searchErr.message && (searchErr.message.includes('404') || searchErr.message.includes("Couldn't load"))) {
                    statusEl.textContent = 'Database not found - please reload the page';
                    resultsEl.innerHTML = '';
                } else {
                    resultsEl.textContent = `Search error: ${searchErr.message}`;
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

        // Check if it's a database loading error (404, etc.)
        if (err.message && (err.message.includes('404') || err.message.includes("Couldn't load"))) {
            statusEl.textContent = 'Database not found - please reload the page';
        } else {
            statusEl.textContent = `Error loading database: ${err.message}`;
        }

        // Disable search functionality when database fails to load
        searchButton.disabled = true;
        searchInput.disabled = true;
        searchInput.placeholder = "Database unavailable";
    }
}

main();
