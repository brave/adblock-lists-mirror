const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');

module.exports = (env) => {
    const dbFilename = process.env.DB_FILENAME || 'rules.db';

    return {
        mode: 'development',
        entry: './search.js',
        output: {
            path: path.resolve(__dirname, 'dist'),
            filename: 'bundle.js',
        },
        plugins: [
            new HtmlWebpackPlugin({
                template: 'index.html',
                templateParameters: {
                    dbUrl: dbFilename,
                },
            }),
            new CopyWebpackPlugin({
                patterns: [
                    { from: 'node_modules/sqlite-wasm-http/deps/dist/sqlite3.wasm', to: 'sqlite3.wasm' },
                    { from: path.resolve(__dirname, dbFilename), to: path.basename(dbFilename) },
                ],
            }),
        ],
    };
};
