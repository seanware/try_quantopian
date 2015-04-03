## Loads data and calcualtes spread

import glob
import os

prefixes = [
		fname.rsplit('_', 1)[-1].split('.')[0]
		for fname in glob.glob(os.path.join(
			"data", "quantquote_daily_sp500_83986", "daily", "*"))]
	
#---------------------CREATE VIEWs ----#
boilerplate =  """
		/* {}
		 *
		 * Automatically generated create statements from\n
		 * group_data_by_columns.py for the s&p500 stock\n
		 * dataset on https://quantquote.com/historical-stock-data\n
		 */ 
		 """
fname = "generated_create_spread_returns_views_sql"
with open(os.path.join("sql", fname), "w") as outfile:
	outfile.write(boilerplate.format(fname))
	outfile.write("""
		CREATE OR REPLACE VIEW spread AS (
			SELECT
		        	h.dt
			""")
	for p in prefixes:
		outfile.write(", (h.{0} - l.{0}) / l.{0} AS {0}\n".format(p))

	outfile.write("""
		FROM high AS h
		JOIN low AS l
			ON h.dt = l.dt
			);
			"""
			)
	outfile.write("\n\n")
	### RETURNS ###
	outfile.write("""
		CREATE OR REPLACE VIEW return AS (
			WITH lag_close AS (
				SELECT dt
				""")

	for p in prefixes:
	    outfile.write(', lag("{0}") OVER (ORDER BY dt) AS "{0}"\n'.format(p))
	 
	outfile.write("""
		FROM close
		)
		SELECT
		c.dt
		"""
		)

	for p in prefixes:
	    outfile.write(",100 * (c.{0} - l.{0}) / l.{0} AS {0}\n".format(p))

	outfile.write("""
		FROM close AS c
		JOIN lag_close AS l
			ON c.dt = l.dt
		ORDER BY dt
		);
		""")






			
			



