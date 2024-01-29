### 1. Top 3 most popular films
```SQL
SELECT original_title, popularity
FROM movies
ORDER BY popularity DESC
LIMIT 3;
```
### 2. Number of films by director
```SQL
SELECT directors.name, COUNT(movies.director_id) AS movies_per_director
FROM directors
INNER JOIN movies ON directors.id = movies.director_id
GROUP BY directors.name
ORDER by movies_per_director DESC;
```
### 3. The top 5 directors to have made a profit during their career
```SQL
SELECT d.name, SUM(m.revenue - m.budget) AS profit
FROM directors d
INNER JOIN movies m  ON d.id = m.director_id
GROUP BY d.name
ORDER by profit DESC
LIMIT 5;
```

### 4. The number of films per director whose popularity is below 10 and the average rating of these films.
```SQL
SELECT d.name, COUNT(m.director_id) AS ranking, ROUND(AVG(m.vote_average),1) AS average_note
FROM directors d
INNER JOIN movies m  ON d.id = m.director_id
WHERE m.popularity < 10
GROUP BY d.name
ORDER by ranking DESC;
```
### 5. Ranking of female directors by number of films, for films with more than 1,000 voters.
```SQL
CREATE VIEW realisatrice_film_votant AS
    SELECT d.name, m.original_title  , m.vote_count
    FROM directors d
    JOIN movies m ON d.id = m.director_id
    WHERE d.gender = 1;

SELECT * FROM realisatrice_film_votant;

SELECT r.name, COUNT(r.original_title) AS number_of_movies
FROM realisatrice_film_votant r
WHERE r.vote_count > 1000
GROUP BY r.name
ORDER by  number_of_movies DESC;
```

### 6. For each director, the top 3 films with an average rating of over 8 made after 2000, based on average rating.
```SQL
SELECT D.name, M.original_title, M.vote_average, RANK() OVER (PARTITION BY D.name ORDER BY M.vote_average DESC) AS Ranking
FROM movies M
INNER JOIN directors D
ON D.id = M.director_id
WHERE M.vote_average > 8 AND M.release_date > 2000
ORDER BY D.name, M.vote_average DESC
```

### 7. For each film with more than 1000 voters, we also want to show the previous film by the same director, its rating and release date.
```SQL
SELECT
	D.name,
	M.original_title,
	M.vote_average,
	M.release_date,
	LAG(M.original_title) OVER(PARTITION BY D.name ORDER BY M.release_date) AS previous_movie,
	LAG(M.vote_average) OVER(PARTITION BY D.name ORDER BY M.release_date) AS previous_score,
	LAG(M.release_date) OVER(PARTITION BY D.name ORDER BY M.release_date) AS previous_date,
	M.vote_average - LAG(M.vote_average, 1, NULL) OVER(PARTITION BY D.name ORDER BY M.release_date) AS diff_score
FROM movies M
INNER JOIN directors D
ON D.id = M.director_id
WHERE M.vote_count > 1000
ORDER BY diff_score DESC;
```
### 8. Addition of an extra column to categorize each film's budget in intervals and we want to know the average budget for each category
```SQL
SELECT *,
ROUND(AVG(budget) OVER(PARTITION BY Budget_Bucket_$)) AS Average_budget_per_cat
FROM (
	SELECT d.name,
	m.original_title,
	m.budget,
	  CASE WHEN m.budget > 0 AND m.budget <= 100 THEN '1$ - 100$'
	   WHEN m.budget > 100 AND m.budget  <= 10000 THEN '100$ - 10k$'
	   WHEN m.budget > 10000 AND m.budget  <= 100000 THEN '10k$ - 100_000k$'
	   WHEN m.budget > 1000000 AND m.budget  <= 100000000 THEN '1M$ - 100M$'
	   WHEN m.budget > 100000000 AND m.budget  <= 250000000 THEN '100M$ - 250M$'
	   ELSE "> 250M$"
	  END Budget_Bucket_$
	  FROM
	  movies m
	      JOIN directors d ON d.id = m.director_id
	      WHERE m.budget > 0
	      )
ORDER BY budget DESC
```

### 9. For each film, the name of the director, the name of the film, the number of voters and the gender. There must also be a column containing the maximum number of voters for a film whose director is male or female.
```SQL
SELECT d.name,m.original_title, m.vote_count, d.gender,
	MAX(m.vote_count) OVER (PARTITION BY d.gender) as max_amount_vote
FROM movies m
JOIN directors d ON d.id = m.director_id
WHERE d.gender IS NOT 0;
```

### 10. Create buckets with almost the same number of films and we'd like to know how many films there are per buckets
```SQL
SELECT Budget_Bucket_$, COUNT(Budget_Bucket_$) as Number_of_movies
FROM (
	SELECT *,
	CASE WHEN percent_ranking >= 0 AND percent_ranking <= 0.2 THEN '0 - 0.2 Percentile'
		   WHEN percent_ranking > 0.2 AND percent_ranking  <= 0.4 THEN '0.2 - 0.4 Percentile'
		   WHEN percent_ranking > 0.4 AND percent_ranking  <= 0.6 THEN '0.4 - 0.6 Percentile'
		   WHEN percent_ranking > 0.6 AND percent_ranking  <= 0.8 THEN '0.6 - 0.8 Percentile'
		   ELSE '0.8 - 1 Percentile'
		  END Budget_Bucket_$
	FROM (
		SELECT d.name,
		m.original_title,
		m.budget,
		PERCENT_RANK() OVER (ORDER BY m.budget) as Percent_ranking
		FROM
		  movies m
		      JOIN directors d ON d.id = m.director_id
		      WHERE m.budget > 0
		      )
		      )
GROUP BY Budget_Bucket_$
```

### 11. Here we'd like to have 5 buckets, where each bucket has [752, 752, 752, 752, 751]films respectively. For each bucket, we want the number of films, the lowest budget for each bucket, the highest budget for each bucket, and finally the average budget for each bucket.
```SQL
SELECT  COUNT(name) as Number_of_movies_per_bucket,
		MIN(budget) as Minimum_budget,
		MAX(budget) as Maximum_budget,
		ROUND(AVG(budget)) as Average_Budget
FROM (
	SELECT d.name,
		m.original_title,
		NTILE(5) OVER(ORDER BY m.budget) AS budget_group,
		budget
	FROM movies m
	JOIN directors d ON d.id = m.director_id
	WHERE budget > 0
	)
GROUP BY budget_group
```
