import pandas as pl


def polars_to_styled_html(df: pl.DataFrame, type: str, max_rows: int = 1000) -> str:
    """Convert Polars DF to styled HTML with Bootstrap classes."""
    
    # Convert to pandas for styling
    pandas_df = df.to_pandas()
    
    # Create styled HTML table
    html = f"""
    <div class="table-responsive" style="max-height: 400px; overflow-y: auto;">
        <table class="table table-sm table-hover table-bordered">
            <thead class="table-light sticky-top">
                <tr>
                    {''.join([f'<th scope="col">{col}</th>' for col in pandas_df.columns])}
                </tr>
            </thead>
            <tbody>
                {pandas_df.head(max_rows).to_html(index=False, header=False, classes='', border=0)
                 .replace('<tr>', '<tr>').replace('</tr>', '</tr>')
                 .replace('<td>', '<td>').replace('</td>', '</td>')}
            </tbody>
        </table>
    </div>
    
    <div class="mt-3">
        <div class="alert alert-secondary py-2">
            <div class="row align-items-center">
                <div class="col">
                    <small>
                        <i class="fas fa-info-circle me-1"></i>
                        Showing {min(max_rows, df.height)} of {df.height} rows, {df.width} columns
                    </small>
                </div>
                <div class="col-auto">
                    <button class="btn btn-sm btn-outline-primary" onclick="exportTable{type}(this)">
                        <i class="fas fa-download me-1"></i> Export
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <script>
    function exportTable() {{
        // Export functionality
        alert('Exporting table...');
    }}
    </script>
    """
    
    return html