### Top 3 most popular films
```SQL
SELECT original_title, popularity
FROM movies
ORDER BY popularity DESC
LIMIT 3;
```
