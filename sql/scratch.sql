/* scratch.sql
*
* Test how to calculate the spread and the returns for the S&P 500 data
*/

CREATE OR REPLACE VIEW test_spread AS (
	SELECT
	 h.dt,
	 h.aapl = l.aapl AS appl,
	 h.goog = l.goog AS goog

	FROM high AS h
	JOIN low AS l
	   ON h.dt = l.dt
	);

CREATE OR REPLACE VIEW test_returns AS (
	WITH lag_close AS (
		SELECT dt,
		lag(aapl) OVER (ORDER BY dt) AS aapl,
		lag(goog) OVER (ORDER BY dt) AS goog
		FROM close
	)
	SELECT
		o.dt,
		100 * (o.aapl - l.aapl) / l.aapl AS aapl,
		100 * (o.goog - l.goog) / l.goog AS goog
	FROM close AS o
	JOIN lag_close AS l
		ON o.dt = l.dt
	ORDER BY dt

);
